// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });

// Import and instantiate the authentication service
const auth = require('../../../auth');
const authService = new auth();

router.get('/', async (req, res) => {
    // Extract the pseudo from the request
    const { pseudo } = req.params;

    // Initialize the user variable because it will be used outside of the try/catch block
    // But it won't be marked as const because it will be reassigned
    let user;

    // Call the getUserByPseudo function from the auth module
    try {
        user = await authService.getUserByPseudo(pseudo);
    }
    catch (err) {
        // If the user is not found, return a 404 instead of a 401
        if (err.message === 'User not found') {
            return res.status(404).json({ error: err.message });
        }
        console.error(err);
        return res.status(401).json({ error: err.message });
    }

    // Extract the public fields from the user
    try {
        const publicUser = authService.getPublicUser(user);
        return res.status(200).json(publicUser);
    }
    catch (err) {
        return res.status(401).json({ error: err.message });
    }
});


// Export the router
module.exports = router;
