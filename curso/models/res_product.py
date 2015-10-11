# -*- coding: utf-8 -*-
#################################################################################

from datetime import datetime

from openerp.osv import fields, osv
import markdown

def generate_html(dict):
    ret = ""
    for data in dict:
        ret += u"<table border=\"0\" cellpadding=\"0\" cellspacing=\"0\">"
        ret += u"	<tbody>"
        ret += u"		<tr>"
        ret += u"			<td>"
        ret += u"			<h2>" + data['titulo'] + "</h2>"
        ret += u"			</td>"
        ret += u"			<td>"
        ret += u"			<h5><sub>&nbsp;cod " + data['codigo'] + "</sub></h5>"
        ret += u"			</td>"
        ret += u"		</tr>"
        ret += u"   </tbody>"
        ret += u"</table>"

        # viene del markdown ya con los <p>
        ret += data['acerca_de']

        ret += u"<p>Duración " + data['duracion_semanas'] + u" semanas, (" + data[
            'horas_catedra'] + u"hs)<br/>"
        ret += u"Modalidad " + data['modalidad'] + "</p>"

        ret += "<table  border=\"0\" cellpadding=\"1\" cellspacing=\"1\" style=\"width: 500px;\">"
        ret += "    <tbody>"
        ret += "        <tr>"
        ret += u"            <td><strong>Inicio</strong></td>"
        ret += u"            <td><strong>Cód</strong></td>"
        ret += u"            <td><strong>Días de cursada</strong></td>"
        ret += u"            <td><strong>Horario</strong></td>"
        ret += "        </tr>"
        for line in data['cursos']:
            ret += "        <tr bgcolor=\"#E0ECF8\">"
            ret += "            <td><span>" + line['inicio'] + "</span></td>"
            ret += "            <td><span>" + line['instancia'] + "</span></td>"
            ret += "            <td><span>" + line['dias'] + "</span></td>"
            ret += "            <td><span>" + line['horario'] + "</span></td>"
            ret += "        </tr>"

        ret += "    </tbody>"
        ret += "</table>"
        ret += "<br>"
        if data['temario']:
            ret += "<h2>Temario</h2>"
            ret += data['temario']

    ret += "<hr/>"

    ret += "<h3 style=\"text-align: left;\">Aranceles</h3>"
    for data in dict:
        if data['cuotas'] == '1':
            ss = data['cuotas'] + " cuota de $" + data['valor']
        else:
            ss = data['cuotas'] + " cuotas de $" + data['valor'] + " c/u"

        ret += u"<p><strong>Matrícula: " + data['matricula'] + "</strong><br />"
        ret += "<strong>Pagos: " + ss + "</strong></p>"


    ret += "<table border=\"0\" cellpadding=\"1\" cellspacing=\"1\" style=\"width: 100%;\">"
    ret += "	<tbody>"
    ret += "		<tr>"
    ret += "			<td>"
    ret += "			<h3 style=\"text-align: left;\">Se entrega certificado</h3>"
    ret += "			<p style=\"text-align: center;\"><img alt=\"\" src=\"https://d3njjcbhbojbot.cloudfront.net/web/images/promos/cdp_cert_logo.png\" style=\"width: 110px; height: 110px;\" /></p>"
    ret += "			<p style=\"text-align: center;\">Materiales inclu&iacute;dos en el costo del curso.</p>"
    ret += "			</td>"
    ret += "		</tr>"
    ret += "</tbody>"
    ret += "</table>"
    ret += "<br>"



    return ret


class product_product(osv.osv):
    _inherit = 'product.product'  # Permite la herencia propiamente dicho del modulo product
    _columns = {
        'tot_hs_lecture': fields.integer('Horas catedra',
                                         help="Cantidad de horas que tiene el curso en total."),
        'classes_per_week': fields.integer('Clases por semana',
                                           help="Cantidad de clases en la semana."),
        'hs_lecture': fields.integer('Horas de clase',
                                     help="Duración de cada una de las clases."),
        'agenda': fields.text('Tema'),
        'no_quotes': fields.integer('Cantidad de cuotas'),

        'default_reply_to': fields.char('Respuesta por defecto', size=64,
                                        help="El mail del organizador, que se pondra en \
                                        el campo de respuesta de todos los mails \
                                        enviados automaticamente en inscripciones \
                                        y confirmaciones de cursos."),
        'default_email_registration': fields.many2one('email.template',
                                                      'Mail de inscripcion',
                                                      help="Selecciona el mail de \
                                                      inscripcion que se enviara a la \
                                                      alumna"),
        'default_email_curso': fields.many2one('email.template', 'Mail de confirmacion',
                                               help="Selecciona el mail de confirmacion \
                                               que se enviara a la alumna en el momento \
                                               de la confirmacion"),
        'default_registration_min': fields.integer('Minimo de alumnas en el curso',
                                                   help="define la cantidad minima de \
                                                   alumnas para arrancar el curso. (Pone \
                                                   cero para no tener en cuenta la regla)"),
        'default_registration_max': fields.integer('Maximo de alumnas en el curso',
                                                   help="Define la cantidad maxima de \
                                                   alumnas que puede tener el curso. \
                                                   (Pone cero para no tener en cuenta \
                                                   la regla)"),
    }
    _defaults = {
        'default_registration_min': 0,
        'default_registration_max': 0,
        'classes_per_week': 1,
        'no_quotes': 1,
        'default_reply_to': "makeoverlabinfo@gmail.com"
    }

    #    _sql_constraints = [('default_code_unique', 'unique (default_code)', 'ya hay un producto con esta referencia.')]

    def d2day(self, date):
        wd = datetime.strftime(datetime.strptime(date, '%Y-%m-%d'), '%w')
        if wd:
            dict = {
                '0': u'Domingo',
                '1': u'Lunes',
                '2': u'Martes',
                '3': u'Miércoles',
                '4': u'Jueves',
                '5': u'Viernes',
                '6': u'Sábado'}
            return dict[wd]
        else:
            return '---'

    def button_generate_doc(self, cr, uid, ids, context=None):
        for prod in self.browse(cr, uid, ids, context=context):

            cursos = []
            if not prod.description:
                prod.description = ""

            instance_pool = self.pool.get('curso.curso')
            records = instance_pool.search(cr, uid,
                                           [('default_code', '=', prod.default_code),
                                            '|',
                                            ('state', '=', 'draft'),
                                            ('state', '=', 'confirm')])
            for inst in instance_pool.browse(cr, uid, records, context=context):
                schedule = ""
                if inst.schedule_1:
                    schedule = inst.schedule_1.name
                cursos.append({'inicio': datetime.strftime(
                    datetime.strptime(inst.date_begin, '%Y-%m-%d'), '%d/%m/%Y'),
                    'instancia': '{}/{:0>2d}'.format(prod.default_code,
                                                     inst.instance),
                    'dias': self.d2day(inst.date_begin),
                    'horario': schedule,
                })
            try:
                weeks = str(
                    (prod.tot_hs_lecture / prod.hs_lecture) / prod.classes_per_week)
            except:
                weeks = "error!"

            # si está vacio trae False y da una excepcion en mark_down
            if not prod.agenda:
                prod.agenda = ""

            data = {
                'titulo': prod.name,
                'codigo': prod.default_code,
                'acerca_de': markdown.markdown(prod.description),
                'duracion_semanas': weeks,
                'horas_catedra': str(prod.tot_hs_lecture),
                'modalidad': str(prod.classes_per_week) + ' clase de ' + str(
                    prod.hs_lecture) + ' hs por semana',
                'cursos': cursos,
                'temario': markdown.markdown(prod.agenda),
                'matricula': 'Bonificada',
                'cuotas': str(prod.no_quotes),
                'valor': str(prod.list_price),
            }

            new_page = {
                'name': prod.name,
                'content': generate_html([data]),
            }

        # Borrar el documento si es que existe
        doc_pool = self.pool.get('document.page')
        records = doc_pool.search(cr, uid, [('name', '=', prod.name)])
        doc_pool.unlink(cr, uid, records)

        # Crear el documento
        self.pool.get('document.page').create(cr, uid, new_page, context=context)

        return True