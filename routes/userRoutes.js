const express = require('express');
const User = require('../models/User');
const router = express.Router();

// Register User
router.post('/register', async (req, res) => {
  console.log("Incoming registration request:", req.body);
  const { name, email, password } = req.body;

  try {
    if (!name || !email || !password) {
      return res.status(400).json({ message: "All fields are required" });
    }

    const newUser = new User({ name, email, password });
    await newUser.save();
    res.status(201).json({ message: "User registered successfully!" });
  } catch (error) {
    console.error("Registration error:", error);
    res.status(500).json({ message: "Error registering user", error });
  }
});

router.get('/test', (req, res) => {
  res.json({ message: "User route is working!" });
});





// Login User
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ email, password });
    if (user) {
      res.status(200).json({ message: 'Login successful', user });
    } else {
      res.status(401).json({ message: 'Invalid credentials' });
    }
  } catch (error) {
    res.status(500).json({ message: 'Error during login', error });
  }
});



module.exports = router;  // ✅ Export the routes properly