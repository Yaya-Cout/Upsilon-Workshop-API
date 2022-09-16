# Upsilon Workshop API

This is the API for the Upsilon Workshop. It is used to manage the workshop's
inventory, and to track the progress of the workshop's projects. It is written
in Javascript, and uses the [Express](http://expressjs.com/) framework. It
uses [Prisma](https://www.prisma.io/) to manage the database. This API is
used by the Upsilon Workshop.

## Getting Started

To get started, you will need to install [Node.js](https://nodejs.org/en/).
Then, you will need to install the dependencies. To do this, run the following
command:

```bash
npm install
```

Then, you will need to create a `.env` file. This file will contain the
environment variables that the API uses. You can use the `.env.example` file
as a template. You will need to set the `DATABASE_URL` environment variable
to the URL of the database that you want to use. You can use default values
for development, but you will need to set the `DATABASE_URL` environment
variable to the URL of the database that you want to use in production.

Then, you will need to generate the Prisma client. To do this, run the
following command:

```bash
npx prisma generate
```

Then, you will need to create the database. To do this, run the following
command:

```bash
npx prisma migrate dev --name init
```

Then, you will need to start the API. To do this, run the following command:

```bash
npm start
```

## Testing

To clear the terminal, reset the database and start the server, run the
following command:

```bash
clear && rm prisma/migrations/ prisma/dev.db prisma/dev.db-journal -f; npx prisma migrate dev --name init && npm start
```

(I know, it's a lot of commands. I'll make a script for this later.)

## Contributing

If you would like to contribute to this project, you can do so by forking the
repository, making your changes, and then submitting a pull request. If you
have any questions, you can contact me on GitHub.

## License

This project is licensed under the AGPL-3.0 License. See the [LICENSE](LICENSE)
file for more details.
