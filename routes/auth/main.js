// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });

// Import the route handlers
router.use('/register', require('./register'));
router.use('/login', require('./login'));
router.use('/logout', require('./logout'));
router.use('/delete-account', require('./delete-account'));
router.use('/userinfo', require('./userinfo'));


// Export the router
module.exports = router;
