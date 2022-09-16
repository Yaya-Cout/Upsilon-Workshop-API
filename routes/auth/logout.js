// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });


// Import and instantiate the authentication service
const auth = require('../../auth');
const authService = new auth();

router.get('/', async (req, res) => {
    const token = req.cookies.authToken;
    // Call the logout function from the auth module
    try {
        // Return an error if the token cookie is not set
        if (!token) {
            throw new Error('No token cookie set');
        }
        // Remove the token cookie
        res.clearCookie('authToken');
        let removeStatus = await authService.logout(req.cookies.authToken);
        // Assert that the token was removed
        if (!removeStatus) {
            throw new Error('Token could not be removed from the database');
        }
        return res.status(200).json({ message: 'Logout successful' });
    }
    catch (err) {
        return res.status(401).json({ error: err.message });
    }
});


// Export the router
module.exports = router;
