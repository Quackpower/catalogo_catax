from odoo import models, api, fields,  exceptions
from datetime import datetime, timedelta

class catalogos_catax(models.Model):
    _name = 'catalogos_catax'
    
    clave = fields.Char(string="Clave", required=True)
    name = fields.Char(string="Nombre categoría", required=True)
    descripcion = fields.Text(string="Texto descriptivo de la categoría, se mostrara al usuario final")
    icono = fields.Binary(string="Icono para la categoría, se mostrara al usuario final")
    detalles = fields.Html(string="Detalles e información especifica de la categoria")
    prioridadCate = fields.Integer(string="Prioridad")

    areas_categoria = fields.One2many('subcategorias_catax.relacion_categoria_areas', 'id_categoria')
    activo   = fields.Boolean(string="Activo", default=True)

    def get_activo(self, params):
        """ Jorge Luis López Cruz 14/10/2020
        Esta funcion es la que marca como activo el contratsta o proveedor en sus respectivos campos de aprovado, especialmente para el modulo de sipco
        """
        self.activo = not self.activo


    @api.model
    def create(self, vals):
        name = vals.get('name')
        clave = vals.get('clave')
        _categoria = self.env['catalogos_catax'].sudo().search([('clave','=', clave)])

        if _categoria:
            raise exceptions.UserError('La clave ya existe.')
        
        return super(catalogos_catax, self).create(vals)

    
    def write(self, vals):
        #if 'clave' in vals:
        #    raise exceptions.Warning("Imposible modificar la clave de la Categoría ya que contiene reportes relacionados.")
        record = super(catalogos_catax, self).write(vals)       
        return record     

class subcategorias_catax(models.Model):
    _name = 'subcategorias_catax'
    clave = fields.Char(string="Clave", required=True)
    name = fields.Char(string="Nombre subcategoría", required=True)
    categoria = fields.Many2one('catalogos_catax', string="Categoría perteneciente", ondelete="cascade")
    descripcion = fields.Text(string="Texto descriptivo de la subcategoría, se mostrara al usuario final")
    prioridadSub = fields.Integer(string="Prioridad")
    activo   = fields.Boolean(string="Activo",  default=True)
    etiquetas = fields.One2many('subcategorias_catax.etiquetas', 'id_tag')
    icono = fields.Binary(string="Icono para la categoría, se mostrara al usuario final")

    def get_activo(self, params):
        """ Jorge Luis López Cruz 14/10/2020
        Esta funcion es la que marca como activo el contratsta o proveedor en sus respectivos campos de aprovado, especialmente para el modulo de sipco
        """
        self.activo = not self.activo

    @api.model
    def create(self, vals):
        name = vals.get('name')
        clave = vals.get('clave')
        _subcategoria = self.env['subcategorias_catax'].sudo().search([('clave','=', clave)])

        if _subcategoria:
            raise exceptions.UserError('La clave ya existe.')
        
        return super(subcategorias_catax, self).create(vals)


    
    def write(self, vals):
        if 'clave' in vals:
            raise exceptions.Warning("Imposible modificar la clave de la SubCategoría ya que contiene reportes relacionados.")
        record = super(subcategorias_catax, self).write(vals)       
        return record     

class subcategorias_catax_etiquetas(models.Model):
    _name = 'subcategorias_catax.etiquetas'
    _rec_name = 'etiqueta'

    id_tag = fields.Many2one('subcategorias_catax', ondelete="cascade")
    etiqueta = fields.Char()


    @api.model
    def create(self, vals):
        try:
            return super(subcategorias_catax_etiquetas, self).create(vals)
        except Exception as er:
            raise exceptions.Warning(str(er))
    
    
    def write(self, vals):
        try:
            return super(subcategorias_catax_etiquetas, self).write(vals)
        except Exception as er:
            raise exceptions.Warning(str(er))

    
    def read(self, fields=None, load='_classic_read'):
        return super(subcategorias_catax_etiquetas, self).read(fields, load=load)
class ayto_folios(models.Model):
    """
        Creado por H.Stivalet
        Fecha de Creación: 2019-10-08
        Descripción: Módulo encargado de almacenar la foliación de registros del Ayuntamiento de Xalapa
    """
    _name = 'subcategorias_catax.folios'             
    _rec_name = 'model_name'

    odoo_model = fields.Many2one('ir.model', string='Modelo de Odoo', required=True, index=True, ondelete="cascade")
    model_name = fields.Char(string="Modelo", related="odoo_model.model", store=True, index=True)
    year = fields.Integer(string="Año", required=True, default=datetime.now().year)
    folio = fields.Integer(string="Folio", required=True, default=1)
    reinicio = fields.Selection([('S','Si'),('N','No')], string="Reinicio", required=True, default='N')

    def get_folio(self, model_name, increase=True):
        """
            Creado por H.Stivalet
            Fecha de Creación: 2019-10-09
            Descripción: Obtiene el consecutivo para un modelo de Odoo
            args:
                model_name(str): Modelo de Odoo (Tabla física de Postgres). No debe ser el Módulo si no el Modelo (usualmente: modulo_odoo.modelo)
                increase(Bool): Incrementa el foliador reservando el folio al registro que lo solicito (enviar false solo para consultar el folio actual)
            return(int): Folio correspondiente del modelo
        """
        try:
            foliador = self.env['subcategorias_catax.folios']
            current_folio = foliador.sudo().search([('model_name','=',model_name)])
            current_year = datetime.now().year
            if not current_folio: # inserta una nueva configuración en el foliador
                # Al no haber registros para el modelo enviado, busca el modelo y lo inserta en el foliador
                model_id = self.env['ir.model'].search([('model','=',model_name)]).id
                if not model_id:
                    raise ValueError('El modelo ' + model_name + ' no fue e contrado en el sistema')
                foliador.sudo().create({
                    'odoo_model': model_id,
                    'model_name': model_name,
                    'year': current_year,
                    'folio': 1,
                    'reinicio': 'N'
                })
                return 1
            elif not increase: # Solo regresa el folio actual
                return current_folio.folio
            else: # Incrementa el foliador y regresa el nuevo folio
                if current_year != current_folio.year:
                    current_folio.year = current_year # Actualiza el año en el foliador
                    if current_folio.reinicio == 'S':
                        current_folio.folio = 1 # Reinicia el Foliador por cambio de año
                    else:
                        current_folio.folio += 1 # Solo incrementa el foliador
                else: # Es el mismo año
                    current_folio.folio += 1 # Incrementa el foliador
                return current_folio.folio
        except Exception as er:
            raise er

class relacion_categoria_areas(models.Model):
    _name = 'subcategorias_catax.relacion_categoria_areas'
    _rec_name = 'id_depto'

    id_categoria = fields.Many2one("catalogos_catax", string="Categoria", ondelete="cascade")
    id_depto     = fields.Many2one("hr.department", ondelete="cascade")  
    
