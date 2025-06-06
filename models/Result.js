const mongoose = require('mongoose');

const resultSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  prediction: { type: String, required: true },
});

const Result = mongoose.model('Result', resultSchema);
module.exports = Result;