# -*- coding: utf-8 -*-
from odoo import http, tools
  # Import the class
from werkzeug.wrappers import Response
import json
import re
import hashlib
import pytz
from datetime import datetime, timedelta
from odoo.http import request
from io import BytesIO
import base64, os
from os.path import dirname
from werkzeug.utils import secure_filename

class CatalogosReporte(http.Controller):
    @http.route('/reporte/categorias_subcategorias/', type='http', auth='public', website=True, cors='*', csrf=False)
    def categorias_subcategorias(self, **kw):
        data = {'status': False}
        try:


            # Obtiene la tabla 
            categorias = http.request.env['catalogos_reporte'].sudo().search([('activo','=', True)], order='prioridadCate asc')
            data['categorias'] = []
            data['subcategorias'] = []

            for x in categorias:
                data['categorias'].append({
                    'categoria' : x.name,
                    'desc' : x.descripcion,
                    'clave' : x.clave,
                    'icono' : str(x.icono),
                    'prioridad': x.prioridadCate,
                    'detalles': x.detalles
                })

                subcategorias = http.request.env['subcategorias_reporte'].sudo().search([('categoria','=',x.name),('activo','=', True)], order='prioridadSub asc')

                for y in subcategorias:
                    etiqueta = []
                    for tt in y['etiquetas']:
                        etiqueta.append({'tag': tt.etiqueta})

                    data['subcategorias'].append({
                        'categorias' : x.name,
                        'clave_cat' : x.clave,
                        'subcategoria' : y.name,
                        'desc' : y.descripcion,
                        'clave' : y.clave,
                        'icono' : str(y.icono),
                        'prioridad': y.prioridadSub,
                        'etiquetas': etiqueta
                    })

           
            data['status'] = True

        except ValueError as er:
            data['status'] = False
            data['error'] = str(er)

        except Exception as er:
            data['status'] = False
            data['error'] = str(er)

        return Response(json.dumps(data), content_type='application/json;charset=utf-8', status=200)

    