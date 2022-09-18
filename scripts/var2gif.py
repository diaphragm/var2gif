import modules.scripts as scripts
import gradio as gr
import os

from modules import processing
from modules.processing import process_images, Processed
from modules.shared import opts, cmd_opts, state
from modules.images import apply_filename_pattern

class Script(scripts.Script):

    def title(self):
        return "var2gif"

    def show(self, is_img2img):
        # return cmd_opts.allow_code
        return True

    def ui(self, is_img2img):
        info = gr.HTML("<p style=\"margin-bottom:0.75em\">Recommended settings: Variation strength: 0.05 (check \"Extra\" in Seed setting)</p>")
        gif_frame_size = gr.Slider(label='Number of gif frames', value=5, minimum=1, maximum=100, step=1)
        duration = gr.Slider(label='Duration between gif frames (milliseconds)', value=60, minimum=1, maximum=500, step=1)
        outdir_gif = gr.Textbox(label='Output directory for gif', value=opts.outdir_extras_samples, lines=1)

        return [info, gif_frame_size, duration, outdir_gif]

    def run(self, p, info, gif_frame_size, duration, outdir_gif):
        # assert cmd_opts.allow_code, '--allow-code option must be enabled'

        processing.fix_seed(p)
        p.batch_size = 1

        # FIXME
        def gif_file_path():
            file_decoration = opts.samples_filename_pattern or "[seed]-[prompt_spaces]"
            file_decoration = apply_filename_pattern(file_decoration, p, p.seed, p.prompt)

            os.makedirs(outdir_gif, exist_ok=True)

            return os.path.join(outdir_gif, f"var2gif-{file_decoration}.gif")

        subseeds = range(p.subseed, p.subseed + gif_frame_size)

        procs = []
        for subseed in subseeds:
            p.subseed = subseed
            procs.append(process_images(p))

        images = list(map(lambda proc: proc.images[0], procs))
        frames = list(map(lambda im: im.quantize(), images))

        frames[0].save(
            gif_file_path(),
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=duration,
            loop=0
        )

        return Processed(p, images, p.seed, "")
