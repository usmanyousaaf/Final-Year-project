import os
import json
import numpy as np
import tensorflow as tf
from tensorflow\.keras.layers import Input, Embedding, LSTM, Dense  # type: ignore
from tensorflow\.keras.models import Model# type: ignore
from tensorflow\.keras.preprocessing.text import Tokenizer# type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences  # type: ignore

# Define paths

good_dir = 'dataset/good'
bad_dir = 'dataset/bad'

def load_data(directory):
	instructions = []
	inputs = []
	outputs = []
	for filename in os.listdir(directory):
		if filename.startswith('.'):  # Skip hidden files
			continue
		try:
			with open(os.path.join(directory, filename), 'r') as file:
				data = json.load(file)
				instructions.append(data.get('instruction', ''))
				inputs.append(data.get('input', ''))
				outputs.append(json.dumps(data.get('output', '')))
		except Exception as e:
			print(f"Error processing file {filename}: {str(e)[:100]}")
	return instructions, inputs, outputs

print("Loading data...")
good_instructions, good_inputs, good_outputs = load_data(good_dir)
bad_instructions, bad_inputs, bad_outputs = load_data(bad_dir)

# Combine datasets

instructions = good_instructions + bad_instructions
inputs = good_inputs + bad_inputs
outputs = good_outputs + bad_outputs

print(f"Loaded {len(instructions)} samples")

# Tokenization setup

tokenizer = Tokenizer(filters='', lower=False)
tokenizer.fit_on_texts(instructions + inputs + outputs)
vocab_size = len(tokenizer.word_index) + 1

# In your training script, after tokenizer.fit_on_texts()

import json

# Save tokenizer configuration

tokenizer_json = tokenizer.to_json()
with open('tokenizer_config.json', 'w') as f:
	f.write(json.dumps(tokenizer_json))

print("Tokenizer config saved successfully!")

# Sequence conversion

def prepare_sequences(texts, max_length):
	seq = tokenizer.texts_to_sequences(texts)
	return pad_sequences(seq, maxlen=max_length, padding='post')

# Calculate maximum sequence length

max_instruction_len = max(len(s.split()) for s in instructions)
max_input_len = max(len(s.split()) for s in inputs)
max_output_len = max(len(s.split()) for s in outputs)
max_length = max(max_instruction_len, max_input_len, max_output_len)

print(f"Maximum sequence length: {max_length}")

# Prepare all sequences

instruction_sequences = prepare_sequences(instructions, max_length)
input_sequences = prepare_sequences(inputs, max_length)
output_sequences = prepare_sequences(outputs, max_length)

# Create decoder sequences (shifted right)

decoder_input_data = output_sequences[:, :-1]
decoder_output_data = output_sequences[:, 1:]

# Pad decoder sequences to match max_length

decoder_input_data = pad_sequences(decoder_input_data, maxlen=max_length, padding='post')
decoder_output_data = pad_sequences(decoder_output_data, maxlen=max_length, padding='post')

# Model parameters

embed_dim = 256
lstm_units = 128

# Encoder

encoder_inputs = Input(shape=(max_length,))
encoder_embed = Embedding(vocab_size, embed_dim)(encoder_inputs)
encoder_lstm, state_h, state_c = LSTM(lstm_units, return_state=True)(encoder_embed)
encoder_states = [state_h, state_c]

# Decoder

decoder_inputs = Input(shape=(max_length,))
decoder_embed = Embedding(vocab_size, embed_dim)(decoder_inputs)
decoder_lstm = LSTM(lstm_units, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_embed, initial_state=encoder_states)
decoder_dense = Dense(vocab_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

# Complete model

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

# Compile with masked loss

def masked_loss(y_true, y_pred):
	mask = tf.math.logical_not(tf.math.equal(y_true, 0))
	loss = tf.keras.losses.sparse_categorical_crossentropy(y_true, y_pred, from_logits=False)
	mask = tf.cast(mask, dtype=loss.dtype)
	loss *= mask
	return tf.reduce_sum(loss) / tf.reduce_sum(mask)

model.compile(optimizer='adam', loss=masked_loss, metrics=['accuracy'])

# Training

print("Starting training...")
history = model.fit(
	[instruction_sequences, decoder_input_data],
	decoder_output_data,
	batch_size=32,
	epochs=10,
	validation_split=0.2,
	verbose=1
)

print("Training completed successfully!")

# Save the entire model

model.save('code_generation_model.keras')

model.save('code_generation_model.h5')

# Optional: Save weights separately

model.save_weights('model_weights.keras')

print("Model saved successfully!")

