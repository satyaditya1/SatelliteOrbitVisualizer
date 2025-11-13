# plots/earth_3d.py
import plotly.graph_objects as go
import numpy as np
from .colors import BG, TEXT, PRIMARY_ACCENT

def build_3d_earth_orbit(xs, ys, zs, sat_name="satellite", animate=False, frame_count=100):
    # Earth mesh
    radius = 6371.0
    theta = np.linspace(0, 2*np.pi, 80)
    phi = np.linspace(0, np.pi, 40)
    th, ph = np.meshgrid(theta, phi)
    X = radius * np.cos(th) * np.sin(ph)
    Y = radius * np.sin(th) * np.sin(ph)
    Z = radius * np.cos(ph)

    fig = go.Figure()

    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Blues',
                             showscale=False, opacity=0.9, hoverinfo='skip', name='Earth'))

    # orbit line
    fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', name=sat_name,
                                line=dict(color=PRIMARY_ACCENT, width=2)))

    # starting marker
    fig.add_trace(go.Scatter3d(x=[xs[0]], y=[ys[0]], z=[zs[0]], mode='markers+text',
                              marker=dict(size=4, color=PRIMARY_ACCENT), text=[sat_name],
                              textposition='top center', showlegend=False))

    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                                aspectmode='data'),
                      paper_bgcolor=BG, plot_bgcolor=BG, font=dict(color=TEXT),
                      margin=dict(l=0, r=0, t=30, b=0))
    return fig
