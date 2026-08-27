import uuid
import subprocess
import paramiko

from langchain.tools import tool


_sessions: dict[str, paramiko.SSHClient] = {}


@tool
def connect(
    host: str,
    username: str,
    password: str,
    port: int = 22,
) -> str:
    """Connect to a remote server using SSH and return the session ID."""

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
    )

    session_id = str(uuid.uuid4())

    _sessions[session_id] = client

    return session_id


@tool
def disconnect(session_id: str) -> str:
    """Disconnect an existing SSH session."""

    client = _sessions.pop(session_id, None)

    if client is None:
        raise ValueError(f"SSH session not found: {session_id}")

    client.close()

    return f"SSH session {session_id} disconnected"


def execute(
    command: str,
    session_id: str | None = None,
) -> dict:
    """
    Execute a command locally or remotely.

    If session_id is None, execute locally.
    Otherwise execute on the corresponding SSH session.
    """
    try:
        if session_id is None:
            return _execute_local(command)

        return _execute_remote(command, session_id)
    except Exception as E:
        return { "error" : str(E)}


def _execute_local(command: str) -> dict:

    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    return {
        "stdout": process.stdout,
        "stderr": process.stderr,
        "exit_code": process.returncode,
    }


def _execute_remote(
    command: str,
    session_id: str,
) -> dict:

    client = _sessions.get(session_id)

    if client is None:
        raise ValueError(f"SSH session not found: {session_id}")

    stdin, stdout, stderr = client.exec_command(command)

    return {
        "stdout": stdout.read().decode("utf-8", errors="replace"),
        "stderr": stderr.read().decode("utf-8", errors="replace"),
        "exit_code": stdout.channel.recv_exit_status(),
    }