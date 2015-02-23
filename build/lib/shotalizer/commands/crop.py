import logging
import random
import uuid

from PIL import Image
from PIL import ImageFilter
from PIL import ImageOps

from shotalizer.commands.base import BaseCommand


class CropCommand(BaseCommand):

    log = logging.getLogger(__name__)

    NCROPS = 16

    def get_parser(self, prog_name):
        parser = super(CropCommand, self).get_parser(prog_name)
        parser.add_argument('img_filename', nargs='?', default='.')
        parser.add_argument('--width', default=150, help="crops should have this width (pixels)")
        parser.add_argument('--height', default=200, help="crops should have this height (pixels)")
        parser.add_argument('--blur', default=2, help="run gaussian blur with this radius (pixels)")
        return parser

    def __crop_filename(self):
        return str(uuid.uuid4()) + ".jpg"

    def take_action(self, parsed_args):
        original = Image.open(parsed_args.img_filename)
        width, height = original.size
        self.log.info('Loaded "{0}": {1}'.format(parsed_args.img_filename, (width, height)))

        outfile = Image.new("RGB", (900, 1100), (255, 255, 255))

        top_o = 75
        left_o = 75
        for i in range(1, self.NCROPS + 1):
            left = random.randint(0, width - parsed_args.width)
            top = random.randint(0, height - parsed_args.height)
            right = left + parsed_args.width
            bottom = top + parsed_args.height
            result = original.crop((left, top, right, bottom))
            result = ImageOps.grayscale(result)
            result = result.filter(ImageFilter.GaussianBlur(float(parsed_args.blur)))
            self.log.debug('Crop "{0}: {1}: {2}"'.format(i, (left, top, right, bottom), result.size))
            outfile.paste(result, (left_o, top_o))
            if i % 4 == 0:
                left_o = 75
                top_o += parsed_args.height + 50
            else:
                left_o += parsed_args.width + 55
        outfile.save('crops.jpg')
        outfile.show()
