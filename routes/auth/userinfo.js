// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });

// Import and instantiate the authentication service
const auth = require('../../auth');
const authService = new auth();

router.get('/', async (req, res) => {
    // Call the getPrivateUser function from the auth module
    try {
        const user = await authService.getPrivateUser(req.cookies.authToken);
        return res.status(200).json(user);
    }
    catch (err) {
        return res.status(401).json({ error: err.message });
    }
});


// Export the router
module.exports = router;
