A Web-based spectrum display server

This is an adapation of https://github.com/jledet/waterfall, inspired
by work from https://github.com/muaddib1984/gr-webspectrum. The web
portion has been re-implemented in FastAPI using Server Side Events
(SSE), which is a simpler implementation than websockets.

## What This Is

This project is a proof-of-concept architectural demonstration. It
implements a robust, production-quality ASGI web back-end to serve
dynamic content to a browser.

It provides a complete framework for hosting a web
application. Consequently, it may appear more complex than you might
expect, at first. However, when you start extending it, I think the
design decisions that have been made will show their value.

It implements a proof-of-concept spectral display with many
features. It supports update rates in excess of most monitors' refresh
rate.

## What This Is Not

This project is not a production-quality web application. There is
just enough web programming to prove the concepts. The spectrum and
waterfall displays are mostly untouched from the original project.

It does not provide any user authentication, so exposure outside your
local machine/network should not be done. You have been
warned. However, adding authentication to a FastAPI application is
very straightforward, so you can get there from here without difficulty.

This project is not everything you would ever want from a web-based
spectral display. Some features are necessarily application-specific
and I haven't imagined your application. Useful features like changing
the radio parameters are left as an exercise for the reader.

# Architecture

This project is designed with strong separation of concerns. The web
application is only concerned with feeding data to the browser to
drive the visualization.

The interface to the frequency source (radio or simulation) is
isolated to a microservice. This facilitates swapping out data sources
without large-scale changes to the infrastructure.

Redis was chosen as the communications channel between the components
because it is trivial to set up, and very fast.

# INSTALLATION

Because the Python dependencies are extensive, this project was
implemented using Poetry. I chose Poetry because its interface is a
bit nicer than virtual environments (spawning a shell is more
intuitive than remembering to activate/deactivate a venv).

Install Poetry with `pip install poetry`.
Install the dependencies: `poetry install`
Start a Poetry shell with `poetry shell`.

# USAGE

There are three components that need to run

 1. Redis. The easiest way to do this is running a Docker
    container. The default configuration points to a locally running
    Redis database:
    `docker run --rm -dt --name redis -p 6379:6379 redis`

 2. The **uvicorn** ASGI server.
    `cd server; uvicorn --host 0.0.0.0 --port 8000 app.main:app`
    This runs in the foreground, and exposes port 8000 (the default)
    on all network interfaces. If you omit the `--host` argument, it
    will default to "localhost". Or, you can specify any IP address
    your computer supports where you want the web server to listen.

    For debugging, the `--reload` flag is very helpful; it causes the
    server to detect modified python files and restart. For
    production, it is a security hole.

  3. The microservice. This is left as an exercise for the reader, so
     the syntax is up to you. A reference (simulator)
     implementation is provided as
     `microservices/simple_sim.py`

     Another (untested) adapter for GNU Radio is provided as
     `microservices/gr_zmq_adapter.py`

Point your webbrowser to http://127.0.0.1:8000/spectral
you will see the spectrum display


CREDITS
All credit for the graphics goes to jledet, thanks for making a simple but elegant web interface
for displaying spectrum.


