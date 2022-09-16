// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });

// Import and instantiate the authentication service
const auth = require('../../auth');
const authService = new auth();

router.post('/', authService.authMiddleware, async (req, res) => {
    // Get the token from the cookie
    const token = req.cookies.authToken;
    // Get the password from the body
    const { password } = req.body;
    // Call the deleteAccount function from the auth module
    try {
        await authService.deleteAccount(token, password);
        // Remove the token cookie
        res.clearCookie('authToken');
        return res.status(200).json({ message: 'Account deleted' });
    }
    catch (err) {
        return res.status(401).json({ error: err.message });
    }
});


// Export the router
module.exports = router;
