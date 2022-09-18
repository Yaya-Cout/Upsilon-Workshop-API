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

// TODO; Try to see if this can be done with a class (authService.authMiddleware),
//       because Express replaces the 'this' keyword with the request object

// Import the required modules
const auth = require('../auth');

// Instantiate the authentication service
const authService = new auth();

/**
 * Middleware to check if the user is logged in
 */
async function loginMiddleware(req, res, next) {
    // Get the token from the request
    const token = req.cookies.authToken;
    // Ensure the token is not empty or undefined
    if (!token) {
        // If the token is not found, return an error
        return res.status(401).json({
            error: 'Token not found'
        });
    }
    // Get the user from the token
    let user;
    try {
        user = await authService.getUserByToken(token);
    } catch (error) {
        // If the token is not valid, return an error
        return res.status(401).json({
            error: error.message
        });
    }
    // Add the user to the request
    req.user = user;
    // Call the next function
    next();
}

// Export the middleware
module.exports = loginMiddleware;
