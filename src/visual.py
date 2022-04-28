import matplotlib.pyplot as plt
import io

from ipywidgets.widgets import interact 

from plotly.tools import FigureFactory as FF
from plotly.offline import iplot

from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from skimage import measure

from PIL import Image


def plot3d(images, image_title, threshold=-300):
    p = images.transpose(2,1,0)
    
    verts, faces, _, _ = measure.marching_cubes(p, threshold)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    
    mesh = Poly3DCollection(verts[faces], alpha=0.70)
    face_color = [0.45, 0.45, 0.75]
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)

    ax.set_xlim(0, p.shape[0])
    ax.set_ylim(0, p.shape[1])
    ax.set_zlim(0, p.shape[2])

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')

    im = Image.open(img_buf)
    im.save(image_title)

    img_buf.close()


def interactive3d(images, threshold, step_size):
  p = images.transpose(2,1,0)
  verts, faces, _, _ = measure.marching_cubes(p, threshold, step_size=step_size, allow_degenerate=True) 
  x, y, z = zip(*verts) 
  colormap = ['rgb(255, 192, 203)','rgb(236, 236, 212)']
  fig = FF.create_trisurf(x=x, y=y, z=z, plot_edges=False, colormap=colormap, simplices=faces, backgroundcolor='rgb(125, 125, 125)', title="Interactive Visualization")
  iplot(fig)


def slider_util(slices, x):
    plt.imshow(slices[x])
    return x


def slider(slices):
    plt.figure(1)
    interact(slider_util, x=(0, len(slices)-1), y=slices)