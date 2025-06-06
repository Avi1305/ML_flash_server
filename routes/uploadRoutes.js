const express = require('express');
const multer = require('multer');
const path = require('path');

const router = express.Router();
const storage = multer.diskStorage({
  destination: './uploads',
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});

const upload = multer({ storage });

router.post('/predict', upload.single('image'), (req, res) => {
  const filePath = req.file.path;
  console.log('File uploaded:', filePath);
  res.status(200).json({ message: 'Image uploaded successfully!', filePath });
});

module.exports = router;