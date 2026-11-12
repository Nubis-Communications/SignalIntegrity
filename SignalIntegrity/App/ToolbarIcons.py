"""Original outline toolbar artwork, rendered with transparent backgrounds."""

# Copyright (c) 2026 Nubis Communications, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from PIL import Image, ImageDraw


ICON_PATHS = {
    'document-new-3': [('line', (6, 21, 6, 3, 14, 3, 19, 8, 19, 21, 6, 21)),
                       ('line', (14, 3, 14, 8, 19, 8)), ('line', (9, 14, 16, 14)),
                       ('line', (12.5, 10.5, 12.5, 17.5))],
    'document-open-2': [('line', (3, 19, 3, 6, 9, 6, 11, 9, 20, 9, 20, 12)),
                        ('line', (3, 19, 7, 12, 22, 12, 18, 19, 3, 19))],
    'document-save-2': [('line', (4, 3, 18, 3, 21, 6, 21, 21, 4, 21, 4, 3)),
                        ('box', (8, 3, 16, 9)), ('box', (8, 14, 17, 21))],
    'edit-3': [('line', (4, 20, 5, 15, 16, 4, 20, 8, 9, 19, 4, 20)),
               ('line', (14, 6, 18, 10))],
    'eye': [('line', (2, 12, 7, 7, 12, 5, 17, 7, 22, 12, 17, 17, 12, 19, 7, 17, 2, 12)),
             ('oval', (9, 9, 15, 15))],
    'edit-add-2': [('line', (4, 12, 20, 12)), ('line', (12, 4, 12, 20))],
    'edit-delete-6': [('boldline', (6, 6, 18, 18)), ('boldline', (18, 6, 6, 18))],
    'up': [('line', (12, 4, 12, 20)), ('line', (6, 10, 12, 4, 18, 10))],
    'down': [('line', (12, 4, 12, 20)), ('line', (6, 14, 12, 20, 18, 14))],
    'draw-line-3': [('line', (4, 18, 4, 12, 20, 12, 20, 6)),
                    ('oval', (2, 16, 6, 20)), ('oval', (18, 4, 22, 8))],
    'edit-copy-3': [('box', (8, 8, 21, 21)), ('line', (16, 8, 16, 3, 3, 3, 3, 16, 8, 16))],
    'object-rotate-left-4': [('arc', (5, 5, 20, 20, 35, 300)),
                             ('line', (4, 4, 4, 10, 10, 10))],
    'object-flip-horizontal-3': [('line', (12, 3, 12, 21)),
                                 ('line', (3, 6, 9, 12, 3, 18, 3, 6)),
                                 ('line', (21, 6, 15, 12, 21, 18, 21, 6))],
    'object-flip-vertical-3': [('line', (3, 12, 21, 12)),
                               ('line', (6, 3, 12, 9, 18, 3, 6, 3)),
                               ('line', (6, 21, 12, 15, 18, 21, 6, 21))],
    'zoom-in-3': [('oval', (3, 3, 16, 16)), ('line', (15, 15, 21, 21)),
                  ('line', (6, 9.5, 13, 9.5)), ('line', (9.5, 6, 9.5, 13))],
    'zoom-out-3': [('oval', (3, 3, 16, 16)), ('line', (15, 15, 21, 21)),
                   ('line', (6, 9.5, 13, 9.5))],
    'edit-move': [('line', (12, 3, 12, 21)), ('line', (3, 12, 21, 12)),
                   ('line', (8, 7, 12, 3, 16, 7)), ('line', (8, 17, 12, 21, 16, 17)),
                   ('line', (7, 8, 3, 12, 7, 16)), ('line', (17, 8, 21, 12, 17, 16))],
    'tooloptions': [('line', (3, 6, 21, 6)), ('line', (3, 12, 21, 12)),
                     ('line', (3, 18, 21, 18)), ('oval', (6, 3, 12, 9)),
                     ('oval', (13, 9, 19, 15)), ('oval', (7, 15, 13, 21))],
    'system-run-3': [('line', (7, 3, 21, 12, 7, 21, 7, 3))],
    'sp-view': [('line', (3, 3, 3, 21, 21, 21)),
                 ('line', (4, 17, 8, 17, 11, 6, 14, 14, 18, 9, 21, 9))],
    'variables-view': [('line', (8, 6, 10, 5, 11, 6, 12, 8, 13, 12, 14, 16, 15, 18, 17, 18, 18, 17)),
                       ('line', (5, 18, 7, 18, 9, 16, 12, 12, 15, 8, 17, 6, 19, 6))],
    'equations-view': [('line', (19, 4, 6, 4, 13, 12, 6, 20, 19, 20))],
    'photo': [('box', (3, 4, 21, 20)), ('oval', (6, 7, 10, 11)),
               ('line', (4, 19, 10, 13, 13, 16, 17, 11, 21, 16))],
    'help-contents-5': [('oval', (2, 2, 22, 22)), ('arc', (8, 5, 16, 13, 180, 450)),
                         ('line', (12, 12, 12, 15)), ('oval', (11, 18, 13, 20))],
    'help-3': [('arc', (7, 3, 17, 13, 180, 450)),
                ('line', (12, 12, 12, 16)), ('oval', (11, 19, 13, 21))],
    'dialog-information-4': [('oval', (2, 2, 22, 22)), ('boldline', (12, 6, 12, 7)),
                             ('line', (9, 11, 12, 11, 12, 18)), ('line', (9, 18, 15, 18))],
    'edit-undo-3': [('line', (3, 11, 15, 11, 20, 15, 20, 20)),
                     ('line', (8, 6, 3, 11, 8, 16))],
    'edit-redo-3': [('line', (21, 11, 9, 11, 4, 15, 4, 20)),
                     ('line', (16, 6, 21, 11, 16, 16))],
}
ICON_PATHS['dialog-question'] = ICON_PATHS['help-contents-5']
ICON_PATHS['info'] = ICON_PATHS['dialog-information-4']
ICON_PATHS['dialog-error'] = [('oval', (2, 2, 22, 22)),
                            ('boldline', (8, 8, 16, 16)), ('boldline', (16, 8, 8, 16))]
ICON_PATHS['dialog-warning'] = [('line', (12, 2, 22, 21, 2, 21, 12, 2)),
                              ('boldline', (12, 8, 12, 14)), ('boldline', (12, 17, 12, 18))]


def RenderToolbarIcon(name, color, size):
    if size <= 0:
        raise ValueError('Toolbar icon size must be positive')
    paths = ICON_PATHS[name]
    supersample = 4
    scale = size * supersample / 24.0
    image = Image.new('RGBA', (size * supersample, size * supersample), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    stroke = max(1, round(1.6 * scale))
    for operation, coordinates in paths:
        positions = coordinates[:4] if operation == 'arc' else coordinates
        points = tuple(round(value * scale) for value in positions)
        if operation in ('line', 'boldline'):
            width = max(1, round(2.8 * scale)) if operation == 'boldline' else stroke
            draw.line(points, fill=color, width=width)
        elif operation == 'box':
            draw.rectangle(points, outline=color, width=stroke)
        elif operation == 'oval':
            draw.ellipse(points, outline=color, width=stroke)
        elif operation == 'arc':
            draw.arc(points, coordinates[4], coordinates[5], fill=color, width=stroke)
        else:
            raise ValueError('Unknown toolbar drawing operation: ' + operation)
    resampling = getattr(Image, 'Resampling', Image).LANCZOS
    return image.resize((size, size), resampling)
