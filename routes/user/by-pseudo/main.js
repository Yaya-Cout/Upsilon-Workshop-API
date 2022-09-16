// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });

// Import the route handlers
router.use('/', require('./index'));

// Export the router
module.exports = router;
