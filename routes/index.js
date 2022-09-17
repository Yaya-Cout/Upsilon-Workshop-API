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

// Import the route handlers
router.use('/', require('./auth/main'));
router.use('/user', require('./user/main'));
router.use('/scripts', require('./scripts/main'));

/* GET home page. */
// TODO: Use OpenAPI to generate this
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


module.exports = router;
