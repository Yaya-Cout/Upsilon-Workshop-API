// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });

// We need to ensure that pseudo is a valid pseudo (non null, non empty, etc.)
router.param('pseudo', (req, res, next, pseudo) => {
    // Check if the pseudo is valid
    if (pseudo === undefined || pseudo === null || pseudo === '') {
        // The pseudo is not valid, return an error
        return res.status(401).json({
            error: 'Invalid pseudo'
        });
    }

    // The pseudo is valid, continue
    next();
});


// Import the route handlers
router.use('/:pseudo', require('./by-pseudo/main'));


// Export the router
module.exports = router;
