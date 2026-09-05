from fastapi import Request


def get_graph(req : Request):
    return req.app.state.graph