const MONGO_URL = "mongodb+srv://admin123:EyeDisease123@cluster0.0dmadoo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
app.use(cors());
app.use(bodyParser.json());






mongoose.connect(MONGO_URL, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('Connected to MongoDB Atlas'))
.catch((err) => console.error('MongoDB connection error:', err));

app.get('/', (req, res) => {
  res.send('Backend is running!');
});

const PORT = 5001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

const userRoutes = require('./routes/userRoutes');
app.use('/api/users', userRoutes);

const uploadRoutes = require('./routes/uploadRoutes');
app.use('/api/uploads', uploadRoutes);

const fs = require('fs');

console.log('Checking routes directory...');
console.log('Routes:', fs.readdirSync('./routes'));  // List all files in 'routes'




