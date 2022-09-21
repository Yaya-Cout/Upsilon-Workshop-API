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

// Import the authentication middleware
const loginMiddleware = require('../authMiddleware');

// Delete a script
router.delete('/:id', loginMiddleware, async (req, res) => {
    // Get the request parameters
    const { id } = req.params;
    const token = req.cookies.authToken;
    // Delete the script
    try {
        await authService.deleteScript(token, id);
        return res.status(200).json({ message: 'Script deleted' });
    } catch (err) {
        return res.status(400).json({ error: err.message });
    }
});


// Export the router
module.exports = router;
