import logging
import os
import random

from PIL import Image
from PIL import ImageFilter
from PIL import ImageOps
from PIL import ImageChops

from shotalizer.commands.base import BaseCommand


class BaseCropMixin(object):

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('img_filename', type=str, nargs='+')
        parser.add_argument('--outputdir', default='outputs', help="where should outputs be written?")
        parser.add_argument('--width', default=150, help="crops should have this width (pixels)", type=int)
        parser.add_argument('--height', default=200, help="crops should have this height (pixels)", type=int)
        parser.add_argument('--blur', default=2, help="run gaussian blur with this radius (pixels)", type=int)
        return parser

    def save(self, outputdir, filename, image):
        basefile, _ = os.path.splitext(os.path.basename(filename))
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)
        i = 0
        while os.path.exists(os.path.join(outputdir, f'{basefile}-{i}.png')):
            i += 1
        image.save(os.path.join(outputdir, f'{basefile}-{i}.png'))

    def _crop(self, parsed_args, original):
        width, height = original.size
        scale = random.uniform(0.2, 3)

        # Calculate the crop points
        crop_width = int(parsed_args.width * scale)
        crop_height = int(parsed_args.height * scale)
        left = random.randint(0, width - crop_width)
        top = random.randint(0, height - crop_height)
        right = left + crop_width
        bottom = top + crop_height

        # Do the crop
        result = original.crop((left, top, right, bottom))
        result = result.resize((parsed_args.width, parsed_args.height))

        # Greyscale it
        result = ImageOps.grayscale(result)

        # Blur
        result = result.filter(ImageFilter.GaussianBlur(float(parsed_args.blur)))
        result = result.filter(ImageFilter.UnsharpMask(float(parsed_args.blur)))

        result = ImageOps.autocontrast(result)
        return(result)


class CropSheetCommand(BaseCropMixin, BaseCommand):

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('--ncrops', default=16, help="This many crops per sheet", type=int)
        parser.add_argument('--merge', default=False, action="store_true", help="Merge several images to make the sheet")
        return parser

    def take_action(self, parsed_args):
        outfile = Image.new(
            "RGB",
            (900, 1100),
            (255, 255, 255)
        )

        xpad = int(((outfile.size[0]-150)/((4*parsed_args.width))/3))
        if xpad < 1:
            xpad = 1
        base_left_o = int((((outfile.size[0] - (4*parsed_args.width)) + xpad))/2)
        left_o = base_left_o
        nrows = int(parsed_args.ncrops/4)
        top_o = int((outfile.size[1]-int((nrows * parsed_args.height) + xpad * (nrows -1)))/2)
        for i in range(1, parsed_args.ncrops + 1):
            if isinstance(parsed_args.img_filename, list):
                filename = random.choice(parsed_args.img_filename)
            else:
                filename = parsed_args.img_filename
            original = Image.open(filename)
            crop = self._crop(parsed_args, original)
            if parsed_args.merge:
                crop = ImageChops.blend(crop, self._crop(parsed_args, original), 0.5)
            outfile.paste(crop, (left_o, top_o))
            if i % 4 == 0:
                left_o = base_left_o
                top_o += parsed_args.height + xpad
            else:
                left_o += parsed_args.width + xpad
        self.save(
            parsed_args.outputdir,
            'gallery',
            outfile
        )
        outfile.show()



class CropCommand(BaseCropMixin, BaseCommand):

    log = logging.getLogger(__name__)


    def take_action(self, parsed_args):
        original = Image.open(parsed_args.img_filename)
        width, height = original.size
        outfile = Image.new("RGB", (900, 1100), (255, 255, 255))
        result = self._crop(parsed_args, original)
        result = result.resize((750, 1000))
        outfile.paste(result, (75, 50))
        outfile.show()
