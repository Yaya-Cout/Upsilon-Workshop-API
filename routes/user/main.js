// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });

// Import the route handlers
router.use('/:pseudo', require('./by-pseudo/main'));


// Export the router
module.exports = router;
