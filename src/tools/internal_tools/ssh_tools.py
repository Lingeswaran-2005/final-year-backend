import uuid
import subprocess
import socket
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

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=10,
        )

        session_id = str(uuid.uuid4())
        _sessions[session_id] = client
        return session_id
    except paramiko.AuthenticationException:
        return "SSH Connection Error: Authentication failed (invalid username or password)."
    except paramiko.SSHException as e:
        return f"SSH Connection Error: {str(e)}"
    except socket.error as e:
        return f"SSH Connection Error: Unable to reach host '{host}:{port}' ({str(e)})."
    except Exception as e:
        return f"SSH Connection Error: {str(e)}"


@tool
def disconnect(session_id: str) -> str:
    """Disconnect an existing SSH session."""

    try:
        client = _sessions.pop(session_id, None)

        if client is None:
            return f"Error: SSH session not found: {session_id}"

        client.close()
        return f"SSH session {session_id} disconnected"
    except Exception as e:
        return f"Error disconnecting SSH session {session_id}: {str(e)}"


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
        return {
            "stdout": "",
            "stderr": str(E),
            "exit_code": -1,
            "error": str(E),
        }


def _execute_local(command: str) -> dict:
    try:
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
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "error": str(e),
        }


def _execute_remote(
    command: str,
    session_id: str,
) -> dict:
    client = _sessions.get(session_id)

    if client is None:
        return {
            "stdout": "",
            "stderr": f"SSH session not found: {session_id}",
            "exit_code": -1,
            "error": f"SSH session not found: {session_id}",
        }

    try:
        command = f"sudo {command}"
        stdin, stdout, stderr = client.exec_command(command, timeout=30)

        stdout_text = stdout.read().decode("utf-8", errors="replace")
        stderr_text = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()

        return {
            "stdout": stdout_text,
            "stderr": stderr_text,
            "exit_code": exit_code,
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "error": str(e),
        }
