# imc.py
# Calculadora de Índice de Masa Corporal para ClinicalAyudante

from gi.repository import Gtk, Adw
import gettext

_ = gettext.gettext

class CalculadoraIMC(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Adw.Clamp asegura que el contenido no se estire demasiado en pantallas anchas
        # La propiedad correcta para GNOME 49 es maximum_size
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
            title=_("Datos Antropométricos"),
            description=_("Ingrese el peso y la talla del paciente. Se permite el uso de coma decimal.")
        )
        box.append(grupo_entrada)

        # Fila para el Peso con sufijo de unidad
        self.fila_peso = Adw.EntryRow(title=_("Peso (kg)"))
        self.fila_peso.add_suffix(Gtk.Label(label="kg", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_peso)

        # Fila para la Altura con sufijo de unidad
        self.fila_altura = Adw.EntryRow(title=_("Altura (m)"))
        self.fila_altura.add_suffix(Gtk.Label(label="m", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_altura)

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Clasificación Nutricional"))
        box.append(grupo_resultado)

        # Contenedor visual para el resultado destacado
        caja_valor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, css_classes=["card"])
        caja_valor.set_margin_top(12)

        # Valor numérico con jerarquía title-1 y color accent de Libadwaita
        self.label_imc = Gtk.Label(label="--.-")
        self.label_imc.add_css_class("title-1")
        self.label_imc.add_css_class("accent")

        # Categoría diagnóstica según la OMS
        self.label_categoria = Gtk.Label(label=_("Esperando datos..."))
        self.label_categoria.add_css_class("caption")
        self.label_categoria.add_css_class("dim-label")

        caja_valor.append(self.label_imc)
        caja_valor.append(self.label_categoria)
        grupo_resultado.add(caja_valor)

        # Botón de acción principal
        boton_calcular = Gtk.Button(
            label=_("Calcular IMC"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton_calcular.set_margin_start(90)
        boton_calcular.set_margin_end(90)
        boton_calcular.connect("clicked", self.calcular)
        box.append(boton_calcular)

    def calcular(self, boton):
        try:
            # Procesamiento de texto: permitimos comas reemplazándolas por puntos
            t_peso = self.fila_peso.get_text().replace(',', '.')
            t_altura = self.fila_altura.get_text().replace(',', '.')

            if not t_peso or not t_altura:
                return

            peso = float(t_peso)
            altura = float(t_altura)

            if altura <= 0:
                raise ValueError

            # Cálculo: IMC = Peso / Altura²
            imc = peso / (altura ** 2)

            # Formateo del resultado para el usuario
            self.label_imc.set_label(f"{imc:.1f}".replace('.', ','))

            # Clasificación diagnóstica básica
            if imc < 18.5:
                cat = _("Bajo peso")
            elif imc < 25:
                cat = _("Peso normal")
            elif imc < 30:
                cat = _("Sobrepeso")
            else:
                cat = _("Obesidad")

            self.label_categoria.set_label(cat)

        except (ValueError, ZeroDivisionError):
            self.label_imc.set_label("--.-")
            self.label_categoria.set_label(_("Entrada no válida"))
