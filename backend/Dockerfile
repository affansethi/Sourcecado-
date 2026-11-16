# The hosted demo backend: one container on Railway.
# Build context is this backend/ directory: `docker build backend`.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# YOUR TURN (block 2, piece 3): write the rest of this file. About 10 lines.
#
# 1. Work in the folder /app                               (WORKDIR)
# 2. Copy the file requirements.lock into it               (COPY)
# 3. Install it:  python -m pip install --require-hashes -r requirements.lock   (RUN)
# 4. Copy the folder coworker into ./coworker              (COPY)
#    Steps 2 and 3 come before step 4, so that a code change does not
#    install everything again.
# 5. In one RUN line: create a user named app with the id 10001
#    (useradd --create-home --uid 10001 app), create the folder /data/club
#    (mkdir -p), and give that folder to app (chown -R app:app).
# 6. Set the variable CLUB_STATE_DIR to /data/club         (ENV)
# 7. Run as the user app                                   (USER)
# 8. Say that the server listens on port 8080              (EXPOSE)
# 9. Start the server. The host must be 0.0.0.0, and the port comes from
#    the variable PORT, or 8080 when PORT is not set:
#      CMD ["sh", "-c", "exec python -m coworker.run --host 0.0.0.0 --port ${PORT:-8080}"]

WORKDIR /app
COPY requirements.lock .
RUN python -m pip install --require-hashes -r requirements.lock
COPY coworker ./coworker
RUN useradd --create-home --uid 10001 app && mkdir -p /data/club && chown -R app:app /data/club
ENV CLUB_STATE_DIR=/data/club
USER app
EXPOSE 8080
CMD ["sh", "-c", "exec python -m coworker.run --host 0.0.0.0 --port ${PORT:-8080}"]