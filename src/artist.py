#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator script for training image-bundles
"""
import numpy as np
import math
import cairo
import pickle


class ImageBundle():
    '''A collection of randomly-generated CustomImages'''
    def __init__(self, batch_size, num_tri, width, height):
        # Bundle individual images (array)
        self.images = np.empty((batch_size, height, width, 1))

        # Bundle the arrays of triangle info as a separate attribute
        self.tri_list = np.empty((batch_size, num_tri, 5, 1))
        for i in range(batch_size):
            new_img = CustomImage(width, height)
            new_img.rand_tri(num_tri)
            self.images[i, :, :, 0] = new_img.img[:, :, 0]  # !!!Red channel
            self.tri_list[i, :, :, 0] = new_img.triangles[:, :]

    def save(self, filepath):
        pickle.dump(self, open(filepath, 'wb'))


class CustomImage():
    '''A randomly-generated image object used to train the NN model
    IN: image width=512px, image height=512px'''
    def __init__(self, width=512, height=512):
        self.WIDTH, self.HEIGHT = width, height
        # Create empty shapelist
        # Each row repr one shape with [pos_x, pos_y, w_scale, h_scale, rot]
        self.triangles = None

        # ??? Store a separate array of shape types?
        # self.shape_types = ...

        # Initialize an array of white RGBA values (4 channel)
        self.img = np.zeros((self.HEIGHT, self.WIDTH, 4), dtype=np.uint8)
        # Initialize a Cairo context and drawing surface
        self.surface = cairo.ImageSurface.create_for_data(
            self.img,
            cairo.FORMAT_ARGB32,
            self.WIDTH, self.HEIGHT)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_source_rgb(1.0, 1.0, 1.0)
        self.ctx.paint()

    def triangle(self):
        '''Create a basic equilateral triangle
        Middle-centered w/ side length 0.25*WIDTH'''
        WIDTH, HEIGHT = self.WIDTH, self.HEIGHT
        ctx = self.ctx
        ctx.move_to(0, -0.144*HEIGHT)
#        ctx.rel_line_to(0.5*math.cos(-math.pi/3),
#                        0.5*math.sin(-math.pi/3))
#        ctx.rel_line_to(-0.5, 0)
        ctx.line_to(0.125*WIDTH, 0.072*HEIGHT)
        ctx.line_to(-0.125*WIDTH, 0.072*HEIGHT)
        ctx.close_path()

    def draw_tri(self, off_x, off_y, w_scale, h_scale, rot):
        ''' Draw a particular triangle using triangle() as a template'''
        ctx = self.ctx
        # Reset drawing transformation and choose black source
        ctx.identity_matrix()
        ctx.set_source_rgb(0.0, 0.0, 0.0)
        # Set drawing transformation, then stamp triangle template
        ctx.translate(off_x, off_y)
        ctx.rotate(rot)
        ctx.scale(w_scale, h_scale)
        self.triangle()
        ctx.fill()

    def rand_tri(self, num_tri):
        '''Draw a particular number of random triangles'''
        WIDTH, HEIGHT = self.WIDTH, self.HEIGHT
        self.triangles = np.empty((num_tri, 5))

        for i in range(num_tri):
            # Randomize drawing params
            off_x = WIDTH * np.random.rand()
            off_y = HEIGHT * np.random.rand()
            w_scale = np.clip(2 * np.random.rand(), 0.1, 4)
            h_scale = np.clip(2 * np.random.rand(), 0.1, 4)
            rot = 2 * math.pi * np.random.rand()

            self.draw_tri(off_x, off_y, w_scale, h_scale, rot)
            self.triangles[i, :] = [off_x, off_y, w_scale, h_scale, rot]


class OutputImage(CustomImage):
    '''A subclass of CustomImage just for displaying model outputs
    IN: image width, image height, Nx5 NumPy array of triangle data'''
    def __init__(self, width, height, triangles):
        super().__init__(width, height)
        self.triangles = triangles

    def display(self):
        '''Display all of the stored shapes'''
        # Reset and clear the drawing surface
        self.ctx.identity_matrix()
        self.ctx.set_source_rgb(1.0, 1.0, 1.0)
        self.ctx.paint()

        # Draw each triangle stored in the triangle array
        for triangle in self.triangles:
            off_x, off_y, w_scale, h_scale, rot = triangle
            self.draw_tri(off_x, off_y, w_scale, h_scale, rot)

        # !!! Save the image to PNG
        self.surface.write_to_png(open('display_test.png', 'wb'))

if (__name__ == '__main__'):
    my_bundle = ImageBundle(25, 5, 512, 512)
    my_bundle.save('../data/train_set_01.pkl')
