from string import Template
import pdb
# Knobs
label_just = 30
type_just = 15
class_just = 10
prio_just = 3
data_just = 7
extra_just = 3

def render_mx(mx_set):
    BUILD_STR = ''
    template = Template("{label:$label_just}{rclass:$class_just}{rtype:$type_just}{prio:$prio_just}{server:$data_just}.\n")
    template = template.substitute(label_just=label_just, class_just=class_just,\
                        type_just=type_just, prio_just=prio_just, data_just=data_just)
    print template

    for mx in mx_set:
        BUILD_STR += "$TTL %s\n" % (mx.ttl)
        label = mx.label if mx.label != '' else '@'
        BUILD_STR += template.format(label=label, rclass='IN', rtype='MX', prio=str(mx.priority),\
                                    server=mx.server)
    return BUILD_STR

def render_ns(nameserver_set):
    BUILD_STR = ''
    template = Template("{label:$label_just}{rclass:$class_just}{rtype:$type_just}{server:$data_just}.\n")
    template = template.substitute(label_just=label_just, class_just=class_just,\
                        type_just=type_just, data_just=data_just)
    for ns in nameserver_set:
        BUILD_STR += template.format(label='@', rclass='IN', rtype='NS', server=ns.server)
    return BUILD_STR

def render_address_record(addressrecord_set):
    BUILD_STR = ''
    template = Template("{label:$label_just}{rclass:$class_just}{rtype:$type_just}{address:$data_just}\n")
    template = template.substitute(label_just=label_just, class_just=class_just,\
                        type_just=type_just, data_just=data_just)
    for rec in addressrecord_set:
        if rec.ip_type == '4':
            rec_type = 'A'
        else:
            rec_type = 'AAAA'
        label = rec.label if rec.label != '' else '@'
        BUILD_STR += template.format(label=label, rclass='IN', rtype=rec_type, address=rec.ip_str)
    return BUILD_STR

def render_cname(cname_set):
    BUILD_STR = ''

    template = Template("{label:$label_just}{rclass:$class_just}{rtype:$type_just}{data:$data_just}.\n")
    template = template.substitute(label_just=label_just, class_just=class_just,\
                        type_just=type_just, data_just=data_just)
    for cname in cname_set:
        label = cname.label if cname.label != '' else '@'
        BUILD_STR += template.format(label=label, rclass='IN', rtype='CNAME', data=cname.data)
    return BUILD_STR

def render_srv(srv_set):
    BUILD_STR = ''
    template = Template("{label:$label_just}{rclass:$class_just}{rtype:$type_just}{prio:$prio_just}{weight:$extra_just}{port:$extra_just}{target:$extra_just}.\n")
    template = template.substitute(label_just=label_just, class_just=class_just,\
                        type_just=type_just, prio_just=prio_just, extra_just=extra_just)
    for srv in srv_set:
        BUILD_STR += template.format(label=srv.label, rclass='IN', rtype='SRV', prio=str(srv.priority), weight=str(srv.weight), port=str(srv.port), target=str(srv.target))
    return BUILD_STR

def render_txt(txt_set):
    BUILD_STR = ''

    template = Template("{label:$label_just}{rclass:$class_just}{rtype:$type_just}\"{data:$data_just}\"\n")
    template = template.substitute(label_just=label_just, class_just=class_just,\
                        type_just=type_just, data_just=data_just)
    for txt in txt_set:
        label = txt.label if txt.label != '' else '@'
        BUILD_STR += template.format(label=label, rclass='IN', rtype='TXT', data=txt.txt_data)
    return BUILD_STR

def render_domain( default_ttl, nameserver_set, mx_set,\
                    addressrecord_set, cname_set, srv_set, txt_set):
    BUILD_STR = ''
    BUILD_STR += render_ns(nameserver_set)
    BUILD_STR += render_mx(mx_set)
    BUILD_STR += render_address_record(addressrecord_set)
    BUILD_STR += render_cname(cname_set)
    BUILD_STR += render_srv(srv_set)
    BUILD_STR += render_txt(txt_set)
    return BUILD_STR
