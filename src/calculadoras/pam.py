# pam.py
# Calculadora de Presión Arterial Media para ClinicalAyudante

from gi.repository import Gtk, Adw
import gettext
import locale

_ = gettext.gettext

class CalculadoraPAM(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Contenedor Clamp para centrar el contenido en pantallas anchas
        clamp = Adw.Clamp(
            maximum_size=600,
            margin_top=32,
            margin_bottom=32,
            margin_start=12,
            margin_end=12
        )
        self.append(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        clamp.set_child(box)

        # --- SECCIÓN DE ENTRADA ---
        grupo_entrada = Adw.PreferencesGroup(
            title=_("Valores de Presión Arterial"),
            description=_("Ingrese los valores en mmHg. Puede usar coma o punto decimal.")
        )
        box.append(grupo_entrada)

        # Fila para Presión Sistólica (PAS)
        self.fila_pas = Adw.EntryRow(title=_("Presión Sistólica (PAS)"))
        self.fila_pas.add_suffix(Gtk.Label(label="mmHg", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_pas)

        # Fila para Presión Diastólica (PAD)
        self.fila_pad = Adw.EntryRow(title=_("Presión Diastólica (PAD)"))
        self.fila_pad.add_suffix(Gtk.Label(label="mmHg", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_pad)

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Resultado"))
        box.append(grupo_resultado)

        # Tarjeta visual para el resultado
        caja_valor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, css_classes=["card"])
        caja_valor.set_margin_top(12)

        self.label_pam = Gtk.Label(label="--")
        self.label_pam.add_css_class("title-1") # Tamaño destacado
        self.label_pam.add_css_class("accent")  # Color azul de énfasis

        self.label_unidad = Gtk.Label(label=_("mmHg"))
        self.label_unidad.add_css_class("caption")
        self.label_unidad.add_css_class("dim-label")

        caja_valor.append(self.label_pam)
        caja_valor.append(self.label_unidad)
        grupo_resultado.add(caja_valor)

        # Botón Calcular
        boton_calcular = Gtk.Button(
            label=_("Calcular PAM"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton_calcular.set_margin_start(90)
        boton_calcular.set_margin_end(90)

        boton_calcular.connect("clicked", self.calcular)
        box.append(boton_calcular)

    def calcular(self, boton):
        try:
            # Procesamiento robusto de decimales con coma o punto
            t_pas = self.fila_pas.get_text().replace(',', '.')
            t_pad = self.fila_pad.get_text().replace(',', '.')

            if not t_pas or not t_pad:
                return

            pas = float(t_pas)
            pad = float(t_pad)

            # Fórmula Médica: PAM = (PAS + 2*PAD) / 3
            pam = (pas + (2 * pad)) / 3

            pam = locale.format_string("%.1f", pam)
            self.label_pam.set_label(pam)

        except (ValueError, ZeroDivisionError):
            self.label_pam.set_label("--")
            # Podríamos añadir un Adw.Toast aquí para errores de entrada
