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
 *
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

const crypto = require('crypto');
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

const passwordConfirmationEnabled = false;
// const TokenExpirationTime = 1000 * 24 * 60 * 60 * 1000; // 24 hours
const TokenExpirationTime = 1000 * 30; // 30 seconds


// Enum type for the user's role
const UserRole = Object.freeze({
    0: 'user',
    1: 'moderator',
    2: 'admin',
});


/**
 * Class to handle authentication
 * @class
 */
class Auth {
    /**
     * Function to initialize the class
     * @constructor
     */
    constructor() {
        // TODO: Use the global prisma instance instead of copying it (even if it's only a reference)
        this.prisma = prisma;
    }

    /**
     * Function to login a user
     * @param {string} email - The email of the user
     * @param {string} password - The password of the user
     * @returns {Promise} - The user object
     * @returns {Promise} - The token object
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name login
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the password is incorrect
     */
    async login(email, password) {
        const user = await this.prisma.user.findUnique({
            where: {
                email: email
            }
        });

        if (!user) {
            throw new Error('User not found');
            // Return the function to prevent security leaks
        }

        if (!this.verifyPassword(password, user.password)) {
            throw new Error('Incorrect password');
            // Return the function to prevent security leaks
            // Disable eslint because the error is thrown on purpose
            // eslint-disable-next-line no-unreachable
            return;
        }
        return await this.generateToken(user);
    }

    /**
     * Function to register a user
     * @param {string} email - The email of the user
     * @param {string} password - The password of the user
     * @param {string} passwordConfirmation - The confirmation of the password
     * @param {string} pseudo - The pseudo of the user
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name register
     * @throws {Error} - If the user already exists
     * @throws {Error} - If the pseudo already exists
     * @throws {Error} - If the password confirmation is incorrect
     */
    async register(email, password, passwordConfirmation, pseudo) {
        const user = await this.prisma.user.findUnique({
            where: {
                email: email
            }
        });

        if (user) {
            throw new Error('User already exists');
        }

        const userPseudo = await this.prisma.user.findUnique({
            where: {
                pseudo: pseudo
            }
        });

        if (userPseudo) {
            throw new Error('Pseudo already exists');
        }

        if (passwordConfirmationEnabled && password !== passwordConfirmation) {
            throw new Error('Password confirmation is incorrect');
        }

        return await this.prisma.user.create({
            data: {
                email: email,
                password: this.hashPassword(password),
                pseudo: pseudo,
            }
        });
    }

    /**
     * Function to remove the token from the database when the user logs out
     * @param {string} token - The token to remove
     * @returns {Promise} - True if the token was removed, false otherwise
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name logout
     */
    async logout(token) {
        // Ensure that the token is a non-empty string, and not null or undefined
        if (!token || typeof token !== 'string') {
            return false;
        }
        const tokenObject = await this.prisma.token.findUnique({
            where: {
                token: token
            }
        });

        if (!tokenObject) {
            return false;
        }

        await this.prisma.token.delete({
            where: {
                token: token
            }
        });

        return true;
    }

    /**
     * Function to delete an account
     * @param {string} token - The token of the user
     * @param {string} password - The password of the user
     * @returns {Promise} - True if the account was deleted, false otherwise
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name deleteAccount
     * @throws {Error} - If the token is invalid
     * @throws {Error} - If the token is expired
     * @throws {Error} - If the token is not found
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the user is an admin
     */
    async deleteAccount(token, password) {
        // Verify the token
        const tokenVerify = await this.verifyToken(token);
        // Crash if the token is invalid
        if (!tokenVerify) {
            throw new Error('Invalid token');
        }
        // Get the user from the token
        const user = await this.getUserFromToken(token);
        // Check if the user exists
        if (!user) {
            throw new Error('User not found');
        }
        // Get the admin key in UserRoles
        const adminKey = Object.keys(UserRole).find(key => UserRole[key] === 'admin');
        // Check if the user is an admin
        if (user.role === adminKey) {
            // If the user is an admin, crash
            throw new Error('Admin accounts cannot be deleted');
        }

        // Check the password
        if (!this.verifyPassword(password, user.password)) {
            throw new Error('Incorrect password');
        }

        // Delete the user
        await this.prisma.token.deleteMany({
            where: {
                userId: user.id
            }
        });
        await this.prisma.user.delete({
            where: {
                id: user.id
            }
        });
        return true;
    }

    /**
     * Function to get public information about a user
     * @param {string} user - The user to get information about (can be a pseudo, an id, or a user object)
     * @returns {Promise} - The user object
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name getUser
     * @throws {Error} - If the user is not found
     */
    async getPublicUser(user) {
        let userObject;
        if (typeof user === 'string') {
            userObject = await this.prisma.user.findUnique({
                where: {
                    OR: [
                        {
                            pseudo: user
                        },
                        {
                            id: user
                        }
                    ]
                }
            });
        } else {
            userObject = user;
        }

        if (!userObject) {
            throw new Error('User not found');
        }

        // Get user privacy settings
        const publicEmail = userObject.publicEmail;
        const publicName = userObject.publicName;
        const publicBirthday = userObject.publicBirthday;
        const publicLocation = userObject.publicLocation;

        // Ensure that they are not null
        if (publicEmail === null) {
            userObject.publicEmail = false;
            // Log a warning
            console.warn(`User ${userObject.pseudo} has a null publicEmail value. This is not allowed, so it has been set to false.`);
        }
        if (publicName === null) {
            userObject.publicName = false;
            // Log a warning
            console.warn(`User ${userObject.pseudo} has a null publicName value. This is not allowed, so it has been set to false.`);
        }
        if (publicBirthday === null) {
            userObject.publicBirthday = false;
            // Log a warning
            console.warn(`User ${userObject.pseudo} has a null publicBirthday value. This is not allowed, so it has been set to false.`);
        }
        if (publicLocation === null) {
            userObject.publicLocation = false;
            // Log a warning
            console.warn(`User ${userObject.pseudo} has a null publicLocation value. This is not allowed, so it has been set to false.`);
        }

        // Now, we can copy the fields we want to return
        const userToReturn = {
            id: userObject.id,
            pseudo: userObject.pseudo,
            email: userObject.publicEmail ? userObject.email : null,
            firstName: userObject.publicName ? userObject.firstName : null,
            lastName: userObject.publicName ? userObject.lastName : null,
            createdAt: userObject.createdAt,
            avatar: userObject.avatar,
            role: userObject.role,
            bio: userObject.bio,
            website: userObject.website,
            location: userObject.publicLocation ? userObject.location : null,
            birthday: userObject.publicBirthday ? userObject.birthday : null,
        };

        return userToReturn;
    }

    /**
     * Function to get private information about a user (requires a token)
     * @param {string} token - The token of the user
     * @returns {Promise} - The user object
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name getPrivateUser
     * @throws {Error} - If the token is invalid
     * @throws {Error} - If the token is expired
     * @throws {Error} - If the token is not found
     * @throws {Error} - If the user is not found
     */
    async getPrivateUser(token) {
        // Verify the token
        const tokenVerify = await this.verifyToken(token);
        // Crash if the token is invalid
        if (!tokenVerify) {
            throw new Error('Invalid token');
        }

        // Get the user from the token
        const user = await this.getUserFromToken(token);
        // Check if the user exists
        if (!user) {
            throw new Error('User not found');
        }

        // We can copy everything except the password
        let userToReturn = user;
        delete userToReturn.password;

        return userToReturn;
    }

    /**
     * Function to delete expired tokens
     * @returns {Promise} - The number of deleted tokens
     * @async
     * @private
     * @memberof Auth
     * @method
     * @name deleteExpiredTokens
     */
    async deleteExpiredTokens() {
        // Tokens are valid for Date.now() + TokenExpirationTime, so, to work with createdAt, we need to substract TokenExpirationTime
        const date = Date.now() - TokenExpirationTime;
        // Convert the date to the "DateTime" format of Prisma
        const dateToPrisma = new Date(date).toISOString();
        const tokens = await this.prisma.token.findMany({
            where: {
                createdAt: {
                    lt: dateToPrisma
                }
            }
        });
        // Get the number of tokens to delete
        const tokensCount = tokens.length;
        // Delete the tokens
        await this.prisma.token.deleteMany({
            where: {
                createdAt: {
                    lt: dateToPrisma
                }
            }
        });

        return tokensCount;
    }

    /**
     * Function to verify a token
     * @param {string} token - The token to verify
     * @returns {boolean} - The result of the verification (true if the token is valid, false otherwise)
     * @public
     * @memberof Auth
     * @method
     * @name verifyToken
     */
    async verifyToken(token) {
        // Ensure the token is not empty or undefined
        if (!token) {
            return false;
        }

        // Get the token from the database
        const tokenObject = await this.prisma.token.findUnique({
            where: {
                token: token
            }
        });
        // Ensure the token exists
        if (!tokenObject) {
            return false;
        }
        // Ensure the token is not expired
        const now = new Date();
        const tokenCreationDate = new Date(token.createdAt);
        const tokenExpirationDate = new Date(tokenCreationDate.getTime() + TokenExpirationTime);
        if (now > tokenExpirationDate) {
            return false;
        }

        // If all the checks are passed, the token is valid
        return true;
    }

    /**
     * Function to get the user from a token
     * @param {string} token - The token to get the user from
     * @returns {Promise} - The user object
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name getUserFromToken
     * @throws {Error} - If the token is not valid
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the token is not found
     * @throws {Error} - If the token is expired
     */
    async getUserFromToken(token) {
        // Ensure the token is valid
        if (!this.verifyToken(token)) {
            throw new Error('Token is not valid');
        }

        // Get the token from the database
        const tokenObject = await this.prisma.token.findUnique({
            where: {
                token: token
            }
        });
        // Ensure the token exists
        if (!tokenObject) {
            // This should never happen because the token is already verified
            // But it's better to be safe than sorry
            throw new Error('Token not found');
        }
        // Get the user from the database
        const user = await this.prisma.user.findUnique({
            where: {
                id: tokenObject.userId
            }
        });
        // Ensure the user exists
        if (!user) {
            // This should never happen because the user must be linked to the token
            // But it's better to check it
            throw new Error('User not found');
        }
        // Return the user
        return user;
    }

    /**
     * Function to get the user from an pseudo
     * @param {string} pseudo - The pseudo to get the user from
     * @returns {Promise} - The user object
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name getUserFromPseudo
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the pseudo is not found
     * @throws {Error} - If the pseudo is not valid
     */
    async getUserByPseudo(pseudo) {
        // Get the user from the database
        const user = await this.prisma.user.findUnique({
            where: {
                pseudo: pseudo
            }
        });
        // Ensure the user exists
        if (!user) {
            // This should never happen because the user must be linked to the token
            // But it's better to check it
            throw new Error('User not found');
        }
        // Return the user
        return user;
    }

    /**
     * Function to get the user from an id
     * @param {string} id - The id to get the user from
     * @returns {Promise} - The user object
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name getUserFromId
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the id is not found
     * @throws {Error} - If the id is not valid
     * @throws {Error} - If the id is not a number
     */
    async getUserById(id) {
        // Check if the id is a valid number
        if (isNaN(id)) {
            throw new Error('Invalid id');
        }

        // Ensure the id is a number
        id = Number(id);

        // Get the user from the database
        const user = await this.prisma.user.findUnique({
            where: {
                id: id
            }
        });

        // Ensure the user exists
        if (!user) {
            throw new Error('User not found');
        }

        // Return the user
        return user;
    }

    /**
     * Get the user's role from an user object
     * @param {object} user - The user object
     * @returns {string} - The user's role
     * @public
     * @memberof Auth
     * @method
     * @name getUserRole
     * @throws {Error} - If the user's role is not found
     * @throws {Error} - If the user's role is not valid
     * @throws {Error} - If the user's role is not found in the enum
     */
    getUserRole(user) {
        // Ensure the user's role is not empty or undefined
        if (!user.role) {
            throw new Error('User role not found');
        }
        // Ensure the user's role is valid
        if (!UserRole.includes(user.role)) {
            throw new Error('User role is not valid');
        }
        // Return the user's role
        return user.role;
    }
    /**
     * Function to get the user's role from a token
     * @param {string} token - The token to get the user's role from
     * @returns {string} - The user's role
     * @public
     * @memberof Auth
     * @method
     * @name getUserRoleFromToken
     * @throws {Error} - If the token is not valid
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the token is not found
     * @throws {Error} - If the token is expired
     * @throws {Error} - If the user's role is not found
     * @throws {Error} - If the user's role is not valid
     * @throws {Error} - If the user's role is not found in the enum
     * @async
     */
    async getUserRoleFromToken(token) {
        // Get the user from the token
        const user = await this.getUserFromToken(token);
        // Get the user's role
        return this.getUserRole(user);
    }

    /**
     * Function to get the user's role from an pseudo
     * @param {string} Pseudo - The pseudo to get the user's role from
     * @returns {string} - The user's role
     * @public
     * @memberof Auth
     * @method
     * @name getUserRoleFromPseudo
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the user's role is not found
     * @throws {Error} - If the user's role is not valid
     * @throws {Error} - If the user's role is not found in the enum
     * @async
     */
    async getUserRoleFromPseudo(Pseudo) {
        // Get the user from the pseudo
        const user = await this.getUserByPseudo(Pseudo);
        // Get the user's role
        return this.getUserRole(user);
    }

    /**
     * Middleware to check if the user is authenticated
     * @param {object} req - The request object
     * @param {object} res - The response object
     * @param {function} next - The next function
     * @public
     * @memberof Auth
     * @method
     * @name authMiddleware
     * @throws {Error} - If the token is not valid
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the token is not found
     * @throws {Error} - If the token is expired
     * @async
     */
    async authMiddleware(req, res, next) {
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
            user = await this.getUserFromToken(token);
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

    /**
     * Function to generate a token
     * @param {string} user - The user object to generate the token from
     * @returns {Promise} - The token object
     * @async
     * @private
     * @memberof Auth
     * @method
     * @name generateToken
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the password is incorrect
     */
    async generateToken(user) {
        const userObjectDatabase = await this.prisma.user.findUnique({
            where: {
                id: user.id,
            }
        });
        // Ensure the user exists
        if (!userObjectDatabase) {
            throw new Error('User not found');
        }

        // Generate the token
        const token = this.generateRandomToken();

        // Create the token in the database
        await this.prisma.user.update({
            where: {
                id: user.id,
            },
            data: {
                Tokens: {
                    create: {
                        token: token,
                        createdAt: new Date(),
                    }
                }
            }
        });

        // Return the token
        return token;
    }

    /**
     * Edit the user's first name
     * @param {string} token - The token of the user
     * @param {string} firstName - The new first name of the user
     * @returns {Promise} - The user object
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name editFirstName
     * @throws {Error} - If the token is not valid
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the token is not found
     * @throws {Error} - If the token is expired
     * @throws {Error} - If the first name is not valid
     * @throws {Error} - If the first name is not a string
     */
    async editFirstName(token, firstName) {
        // Ensure the first name is valid (not empty or undefined, and a string)
        if (!firstName || typeof firstName !== 'string') {
            throw new Error('First name is not valid');
        }
        // Get the user from the token
        const user = await this.getUserFromToken(token);
        // Edit the user's first name
        const updatedUser = await this.prisma.user.update({
            where: {
                id: user.id
            },
            data: {
                firstName
            }
        });
        // Return the updated user
        return updatedUser;
    }

    /**
     * Edit the user's last name
     * @param {string} token - The token of the user
     * @param {string} lastName - The new last name of the user
     * @returns {Promise} - The user object
     * @async
     * @public
     * @memberof Auth
     * @method
     * @name editLastName
     * @throws {Error} - If the token is not valid
     * @throws {Error} - If the user is not found
     * @throws {Error} - If the token is not found
     * @throws {Error} - If the token is expired
     * @throws {Error} - If the last name is not valid
     * @throws {Error} - If the last name is not a string
     */
    async editLastName(token, lastName) {
        // Ensure the last name is valid (not empty or undefined, and a string)
        if (!lastName || typeof lastName !== 'string') {
            throw new Error('Last name is not valid');
        }
        // Get the user from the token
        const user = await this.getUserFromToken(token);
        // Edit the user's last name
        const updatedUser = await this.prisma.user.update({
            where: {
                id: user.id
            },
            data: {
                lastName
            }
        });
        // Return the updated user
        return updatedUser;
    }

    /**
     * Function to generate a random token
     * @returns {string} - The random token
     * @private
     * @memberof Auth
     * @method
     * @name generateRandomToken
     */
    generateRandomToken() {
        return crypto.randomBytes(32).toString('hex');
    }

    /**
     * Function to hash a password
     * @param {string} password - The password to hash
     * @returns {string} - The hashed password
     * @private
     * @memberof Auth
     * @method
     * @name hashPassword
     * @throws {Error} - If the password is not a string
     * @throws {Error} - If the password is empty
     */
    hashPassword(password) {
        if (typeof password !== 'string') {
            throw new Error('Password must be a string');
        }

        if (!password) {
            throw new Error('Password cannot be empty');
        }

        return crypto.createHash('sha256').update(password).digest('base64');
        // return crypto.createHash('sha256').update(password).digest('hex')
    }

    /**
     * Function to verify a password
     * @param {string} password - The password to verify
     * @param {string} hash - The hash to verify
     * @returns {boolean} - The result of the verification
     * @private
     * @memberof Auth
     * @method
     * @name verifyPassword
     * @throws {Error} - If the password is not a string
     * @throws {Error} - If the password is empty
     * @throws {Error} - If the hash is not a string
     * @throws {Error} - If the hash is empty
     * @throws {Error} - If the hash is not a hash
     */
    verifyPassword(password, hash) {
        if (typeof password !== 'string') {
            throw new Error('Password must be a string');
        }

        if (!password) {
            throw new Error('Password cannot be empty');
        }

        if (typeof hash !== 'string') {
            throw new Error('Hash must be a string');
        }

        if (!hash) {
            throw new Error('Hash cannot be empty');
        }

        if (hash.length !== 44) {
            throw new Error('Hash is not a valid hash');
        }

        return this.hashPassword(password) === hash;
    }

}

async function deleteExpiredTokensHelper() {
    let authService = new Auth();
    let deleted = await authService.deleteExpiredTokens();
    if (deleted) {
        console.log(`Deleted ${deleted} expired tokens`);
    }
    // Delete the auth service instance to free up memory
    authService = null;
}

// Run deleteExpiredTokens every 5 minutes
setInterval(deleteExpiredTokensHelper, 300000);

// Run deleteExpiredTokens on startup
deleteExpiredTokensHelper();

// Close the database connection when the process is closed
process.on('SIGINT', () => {
    console.log('Closing database connection...');
    prisma.$disconnect();
    console.log('Database connection closed, exiting...');

    process.exit();
});

module.exports = Auth;