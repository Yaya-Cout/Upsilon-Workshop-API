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
