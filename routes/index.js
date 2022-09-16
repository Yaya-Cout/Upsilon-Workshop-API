/**
 * Upsilon Workshop API
 * Copyright (C) 2022 Upsilon
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

var express = require('express');
var router = express.Router();
const auth = require('../auth');

/* GET home page. */
router.get('/', function(req, res) {
    // Return a JSON list of the API endpoints
    res.json({
        'endpoints': [
            { 'method': 'post', 'path': '/login', 'description': 'Start a session with credentials' },
            { 'method': 'get', 'path': '/logout', 'description': 'End a session' },
            { 'method': 'post', 'path': '/register', 'description': 'Create a new user' },
            { 'method': 'get', 'path': '/scripts', 'description': 'Get a list of scripts' },
            { 'method': 'get', 'path': '/scripts/:id', 'description': 'Get a script by ID' },
            { 'method': 'get', 'path': '/user/:id', 'description': 'Get a user by ID' },
            { 'method': 'get', 'path': '/user/:id/scripts', 'description': 'Get a list of scripts by user ID' },
            { 'method': 'get', 'path': '/settings', 'description': 'Get the user settings' }
        ]
    });
});


router.post('/register', async (req, res) => {
    const { email, firstName, lastName, password, confirmPassword, pseudo } = req.body;
    let user;
    let token;

    // Instantiate a new authentication service
    const authService = new auth();

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

router.post('/login', async (req, res) => {
    const { email, password } = req.body;
    // Instantiate a new authentication service
    const authService = new auth();
    // Call the login function from the auth module
    try {
        // Tell to eslint to ignore the unused variable (user)
        // eslint-disable-next-line no-unused-vars
        const token = await authService.login(email, password);
        // Add the token cookie
        res.cookie('authToken', token, { httpOnly: true });
        return res.status(200).json({ message: 'Login successful' });
    }
    catch (err) {
        return res.status(401).json({ error: err.message });
    }
});

router.get('/logout', async (req, res) => {
    // Instantiate a new authentication service
    const authService = new auth();
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

router.post('/delete-account', async (req, res) => {
    // Get the token from the cookie
    const token = req.cookies.authToken;
    // Get the password from the body
    const { password } = req.body;
    // Instantiate a new authentication service
    const authService = new auth();
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

router.get('/userinfo', async (req, res) => {
    // Instantiate a new authentication service
    const authService = new auth();
    // Call the getPrivateUser function from the auth module
    try {
        const user = await authService.getPrivateUser(req.cookies.authToken);
        return res.status(200).json(user);
    }
    catch (err) {
        return res.status(401).json({ error: err.message });
    }
});

router.get('/user/by-id/:id', async (req, res) => {
    // Extract the id from the request
    const { id } = req.params;
    // Instantiate a new authentication service
    const authService = new auth();

    // Initialize the user variable because it will be used outside of the try/catch block
    // But it won't be marked as const because it will be reassigned
    let user;

    // Call the getUserById function from the auth module
    try {
        user = await authService.getUserFromId(id);
    }
    catch (err) {
        // If the user is not found, return a 404 instead of a 401
        if (err.message === 'User not found') {
            return res.status(404).json({ error: err.message });
        }
        return res.status(401).json({ error: err.message });
    }

    // Extract the public fields from the user
    try {
        const publicUser = authService.getPublicUser(user);
        return res.status(200).json(publicUser);
    }
    catch (err) {
        return res.status(400).json({ error: err.message });
    }

});

router.get('/user/by-pseudo/:pseudo', async (req, res) => {
    // Extract the pseudo from the request
    const { pseudo } = req.params;
    // Instantiate a new authentication service
    const authService = new auth();

    // Initialize the user variable because it will be used outside of the try/catch block
    // But it won't be marked as const because it will be reassigned
    let user;

    // Call the getUserByPseudo function from the auth module
    try {
        user = await authService.getUserFromPseudo(pseudo);
    }
    catch (err) {
        // If the user is not found, return a 404 instead of a 401
        if (err.message === 'User not found') {
            return res.status(404).json({ error: err.message });
        }
        return res.status(401).json({ error: err.message });
    }

    // Extract the public fields from the user
    try {
        const publicUser = authService.getPublicUser(user);
        return res.status(200).json(publicUser);
    }
    catch (err) {
        return res.status(400).json({ error: err.message });
    }
});


module.exports = router;
