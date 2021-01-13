from IPython.display import HTML
from jinja2 import Template
import json
import os
from textwrap import dedent
from uuid import uuid4
from .base_plotter import IPlotter


class ChartJSPlotter(IPlotter):
    """Class for creating Charts.js charts in """

    chartjs_cdn = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.bundle.min.js'

    template = """
    <canvas name='{{chart_name}}' id='{{chart_id}}'></canvas>
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
                      filename='chart',
                      overwrite=True):
        """Save and output the rendered HTML"""

        self.save(data, chart_type, options, filename, overwrite)
        return HTML(filename + '.html')

    def plot(self, data, chart_type, options=None):
        """Output the rendered HTML"""

        return HTML(self.render(data, chart_type, options))

    def save(self,
             data,
             chart_type,
             options=None,
             filename='chart',
             overwrite=True):
        """Save the rendered HTML in the same directory as the notebook"""

        html = self.render(data, chart_type, options, filename)

        if overwrite:
            with open(filename.replace(" ", "_") + '.html', 'w') as f:
                f.write(html)
        else:
            if not os.path.exists(filename.replace(" ", "_") + '.html'):
                with open(filename.replace(" ", "_") + '.html', 'w') as f:
                    f.write(html)
            else:
                raise IOError('File already exists!')
