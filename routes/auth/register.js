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
