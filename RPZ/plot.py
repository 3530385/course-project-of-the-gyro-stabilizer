import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


#wy=np.linspace(-24.5, 24.5, 211)
#wz=np.linspace(-29.4, 29.4, 211)

alpha,beta=np.linspace(-50/180*np.pi, 50/180*np.pi, 500),np.linspace(-50/180*np.pi, 50/180*np.pi, 500)
A,B=np.meshgrid(alpha,beta)


def Wmaxp(A,B):
    g=9.8
    WY,WZ=24.5,-29.4
    return abs((WY-g)*np.cos(B)-WZ*np.sin(B)*np.cos(A))

wmaxp=Wmaxp(A,B)
print(max([max(i) for i in wmaxp]))
x = A
y = B
z = wmaxp

fig = go.Figure()
fig.add_trace(go.Surface(x=x, y=y, z=z, colorbar_x=0, contours = {"z": {"show": True}},colorscale = 'Viridis'))

fig.update_layout(scene = dict(
                    xaxis_title=r'alpha',
                    yaxis_title='beta',
                    zaxis_title='Wyпmax'),
                    width=700,
                    margin=dict(r=20, b=10, l=10, t=10))
fig.update_traces(hoverinfo="all", hovertemplate=r"alpha: %{x}<br> beta: %{y}<br> Wyпmax: %{z}")

fig.show()
