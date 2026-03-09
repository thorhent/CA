# framingham.py
# Calculadora de Riesgo Cardiovascular (Framingham) para ClinicalAyudante

from gi.repository import Gtk, Adw
import math
import gettext

_ = gettext.gettext

class CalculadoraFramingham(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # 1. Crear la barra de desplazamiento
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)
        # "never" en horizontal para evitar scroll lateral innecesario
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.append(self.scroll)

        # 2. El Clamp ahora es hijo del ScrolledWindow
        clamp = Adw.Clamp(
            maximum_size=600,
            margin_top=12,
            margin_bottom=24,
            margin_start=12,
            margin_end=12
        )
        self.scroll.set_child(clamp)



        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        clamp.set_child(box)

        # --- SECCIÓN DE ENTRADA ---
        grupo_entrada = Adw.PreferencesGroup(
            title=_("Perfil de Riesgo"),
            description=_("Estimación de riesgo cardiovascular a 10 años.")
        )
        box.append(grupo_entrada)

        self.fila_edad = Adw.EntryRow(title=_("Edad"))
        self.fila_edad.add_suffix(Gtk.Label(label=_("años"), css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_edad)

        self.fila_col_total = Adw.EntryRow(title=_("Colesterol Total"))
        self.fila_col_total.add_suffix(Gtk.Label(label="mg/dL", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_col_total)

        self.fila_hdl = Adw.EntryRow(title=_("Colesterol HDL"))
        self.fila_hdl.add_suffix(Gtk.Label(label="mg/dL", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_hdl)

        self.fila_pas = Adw.EntryRow(title=_("Presión Sistólica (PAS)"))
        self.fila_pas.add_suffix(Gtk.Label(label="mmHg", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_pas)

        self.fila_sexo = Adw.ComboRow(
            title=_("Sexo"),
            model=Gtk.StringList.new([_("Femenino"), _("Masculino")])
        )
        grupo_entrada.add(self.fila_sexo)

        self.fila_fumador = Adw.ComboRow(
            title=_("Fumador"),
            model=Gtk.StringList.new([_("No"), _("Sí")])
        )
        grupo_entrada.add(self.fila_fumador)

        self.fila_tratamiento = Adw.ComboRow(
            title=_("Tratamiento para HTA"),
            model=Gtk.StringList.new([_("No"), _("Sí")])
        )
        grupo_entrada.add(self.fila_tratamiento)

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Riesgo Estimado"))
        box.append(grupo_resultado)

        caja_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, css_classes=["card"])
        caja_res.set_margin_top(12)

        self.label_riesgo = Gtk.Label(label="--", css_classes=["title-1", "accent"])
        self.label_unidad = Gtk.Label(label="%", css_classes=["caption", "dim-label"])

        caja_res.append(self.label_riesgo)
        caja_res.append(self.label_unidad)
        grupo_resultado.add(caja_res)

        # Fila de interpretación del riesgo
        self.fila_interpretacion = Adw.ActionRow(
            title=_("Nivel de Riesgo"),
            subtitle=_("Pendiente de cálculo")
        )
        grupo_resultado.add(self.fila_interpretacion)

        # Botón de cálculo
        boton = Gtk.Button(
            label=_("Calcular Riesgo"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton.set_margin_start(90)
        boton.set_margin_end(90)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        try:
            # Procesamiento de entradas (mismo que el anterior)
            edad = float(self.fila_edad.get_text().replace(',', '.'))
            col_t = float(self.fila_col_total.get_text().replace(',', '.'))
            hdl = float(self.fila_hdl.get_text().replace(',', '.'))
            pas = float(self.fila_pas.get_text().replace(',', '.'))

            es_masculino = self.fila_sexo.get_selected() == 1
            es_fumador = self.fila_fumador.get_selected() == 1
            en_tratamiento = self.fila_tratamiento.get_selected() == 1

            # Lógica de Framingham (abreviada para el ejemplo)
            if es_masculino:
                ln_edad = 3.06117 * math.log(edad)
                ln_col_t = 1.12370 * math.log(col_t)
                ln_hdl = -0.93263 * math.log(hdl)
                ln_pas = (1.99881 if en_tratamiento else 1.93303) * math.log(pas)
                f_fumador = 0.65451 if es_fumador else 0
                suma = ln_edad + ln_col_t + ln_hdl + ln_pas + f_fumador - 23.9802
                riesgo_val = 1 - (0.88936 ** math.exp(suma))
            else:
                ln_edad = 2.32888 * math.log(edad)
                ln_col_t = 1.20904 * math.log(col_t)
                ln_hdl = -0.70833 * math.log(hdl)
                ln_pas = (2.82263 if en_tratamiento else 2.76157) * math.log(pas)
                f_fumador = 0.52873 if es_fumador else 0
                suma = ln_edad + ln_col_t + ln_hdl + ln_pas + f_fumador - 26.1931
                riesgo_val = 1 - (0.95012 ** math.exp(suma))

            porcentaje = riesgo_val * 100
            self.label_riesgo.set_label(f"{porcentaje:.1f}".replace('.', ','))

            # Interpretación clínica
            if porcentaje < 5:
                nivel = _("Bajo")
                color = "success"
            elif porcentaje < 20:
                nivel = _("Intermedio")
                color = "warning"
            else:
                nivel = _("Alto")
                color = "error"

            self.fila_interpretacion.set_subtitle(nivel)

            # Limpiar clases anteriores y aplicar color visual
            self.label_riesgo.remove_css_class("success")
            self.label_riesgo.remove_css_class("warning")
            self.label_riesgo.remove_css_class("error")
            self.label_riesgo.add_css_class(color)

        except (ValueError, ZeroDivisionError):
            self.label_riesgo.set_label("--")
            self.fila_interpretacion.set_subtitle(_("Error en los datos"))
