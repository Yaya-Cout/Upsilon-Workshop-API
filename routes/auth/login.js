// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });

// Import and instantiate the authentication service
const auth = require('../../auth');
const authService = new auth();

router.post('/', async (req, res) => {
    const { email, password } = req.body;
    // Call the login function from the auth module
    try {
        const token = await authService.login(email, password);
        // Add the token cookie
        res.cookie('authToken', token, { httpOnly: true });
        return res.status(200).json({ message: 'Login successful' });
    }
    catch (err) {
        return res.status(401).json({ error: err.message });
    }
});


// Export the router
module.exports = router;
