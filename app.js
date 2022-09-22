var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
// Handle async errors
require('express-async-errors');

var indexRouter = require('./routes/index');

var app = express();

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
    next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
    // set locals, only providing error in development
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};

    // In development, log the error to the console
    if (req.app.get('env') === 'development') {
        console.error(err);
    }

    if (res.headersSent) {
        return next(err);
    }

    // Return a JSON response with the error message
    res.status(err.status || 500);
    // In production, don't send the error message, just Internal Server Error
    res.json({ error: req.app.get('env') === 'development' ? err.message : 'Internal Server Error' });
});

module.exports = app;
