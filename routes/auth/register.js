// Import the required modules
const express = require('express');
const router = express.Router({ mergeParams: true });


// Import and instantiate the authentication service
const auth = require('../../auth');
const authService = new auth();

router.post('/', async (req, res) => {
    const { email, firstName, lastName, password, confirmPassword, pseudo } = req.body;
    let user;
    let token;

    // Call the register function from the auth module
    try {
        user = await authService.register(email, password, confirmPassword, pseudo);
        // Assert that the user was created
        if (!user || !user.id) {
            throw new Error('User could not be created');
        }
    } catch (err) {
        return res.status(400).json({ error: err.message });
    }
    // From now on, the user is created, but not logged in, so we log them in
    try {
        token = await authService.login(email, password);
        // Add the token cookie
        res.cookie('authToken', token, { httpOnly: true });
    }
    catch (err) {
        return res.status(400).json({ error: err.message });
    }
    // Now, the user is logged in, so we can set the other fields
    try {
        if (firstName) {
            await authService.editFirstName(token, firstName);
        }
        if (lastName) {
            await authService.editLastName(token, lastName);
        }
        user = await authService.getUserFromToken(token);
        return res.status(201).json({ message: 'User created' });
    }
    catch (err) {
        return res.status(400).json({ error: err.message });
    }
});


// Export the router
module.exports = router;
