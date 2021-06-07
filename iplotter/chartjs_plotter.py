from IPython.display import Image, HTML
from jinja2 import Template
import json
import os
from textwrap import dedent
from uuid import uuid4
from .base_plotter import IPlotter
from .export import VirtualBrowser


class ChartJSPlotter(IPlotter):
    """Class for creating Charts.js charts in """

    chartjs_cdn = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.bundle.min.js'
    requirejs_cdn = "'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js'"

    template = """
    <div>
        <canvas name='{{chart_name}}' id='{{chart_id}}'></canvas>
    </div>
    <script>
        require.config({
            paths: {
                chartjs: '{{chartjs_cdn}}'
            }
        });

        require(['chartjs'], function(Chart) {
            const ctx = document.getElementById('{{chart_id}}').getContext('2d');
            new Chart(ctx,{ type: '{{chart_type}}', data: {{data}}, options: {{options}} });
        });
    </script>
    """

    def __init__(self):
        super(ChartJSPlotter, self).__init__()

    def render(self,
               data,
               chart_type,
               options=None,
               chart_name='chart'):
        """Render the data using the HTML template"""

        if self.chartjs_cdn.endswith('.js'):
            self.chartjs_cdn = self.chartjs_cdn[:-3]

        return Template(dedent(self.template)).render(
            chart_id=str(uuid4()),
            chart_name=chart_name,
            chartjs_cdn=self.chartjs_cdn,
            data=json.dumps(
                data, indent=4).replace("'", "\\'").replace('"', "'"),
            chart_type=chart_type,
            options=json.dumps(
                options, indent=4).replace("'", "\\'").replace('"', "'"))

    def plot_and_save(self,
                      data,
                      chart_type,
                      options=None,
                      as_image=False,
                      image_width=960,
                      image_height=480,
                      filename='chart',
                      overwrite=True):
        """Save and output the rendered HTML or image"""

        self.save(data, chart_type, options, as_image,
                  image_width, image_height, filename, overwrite)

        if as_image:
            with open(filename + '.png', 'rb') as image:
                image_b64 = bytearray(image.read())

            return Image(image_b64)

        return HTML(filename + '.html')

    def plot(self,
             data,
             chart_type,
             options=None,
             as_image=False,
             image_width=960,
             image_height=480):
        """Output the rendered HTML or image"""

        if as_image:
            self.save(data, chart_type, options,
                      as_image, image_width, image_height)

            with open('chart.png', 'rb') as image:
                image_b64 = bytearray(image.read())

            os.remove('chart.png')
            return Image(image_b64)

        return HTML(self.render(data, chart_type, options))

    def save(self,
             data,
             chart_type,
             options=None,
             as_image=False,
             image_width=960,
             image_height=480,
             filename='chart',
             overwrite=True,
             keep_html=False):
        """Save the rendered HTML or image"""

        html = self.render(data, chart_type, options, filename)

        filename = filename.replace(" ", "_")

        html = '\n'.join(('<script src={}></script>'.format(self.requirejs_cdn), html))

        if overwrite or not os.path.exists(filename + '.html'):
            with open(filename.replace(" ", "_") + '.html', 'w') as f:
                f.write(html)
        else:
            raise IOError('File already exists: {}.html'.format(filename))

        if as_image:
            if overwrite or not os.path.exists(filename + '.png'):
                with VirtualBrowser() as browser:
                    browser.save_as_png(filename, image_width, image_height)
            else:
                raise IOError('File already exists: {}.png'.format(filename))

            if not keep_html:
                os.remove(filename + '.html')
