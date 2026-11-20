import sys
import datetime
import logging

# Configura la salida estándar en UTF-8 para evitar errores de tildes en consola (Windows)
sys.stdout.reconfigure(encoding='utf-8')

# 1. Configuración del sistema de logs para registrar eventos y errores en archivo
logging.basicConfig(
    filename='sistema_errores.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


# 2. Excepciones personalizadas del dominio de Software FJ
class ClienteNoEncontradoException(Exception):
    """Excepción lanzada cuando no se encuentra un cliente registrado."""
    pass


class ServicioNoDisponibleException(Exception):
    """Excepción lanzada cuando un servicio no está disponible o tiene parámetros inválidos."""
    pass


class ReservaInvalidaException(Exception):
    """Excepción lanzada cuando una reserva no cumple las condiciones requeridas."""
    pass


# 3. Clase abstracta general para entidades del sistema
class EntidadBase:
    """Representa una entidad genérica con identificador encapsulado."""

    def __init__(self, identificador: str):
        # Valida que el identificador sea una cadena no vacía
        if not identificador or not identificador.strip():
            raise ValueError("El identificador no puede estar vacío.")
        self._identificador = identificador.strip()

    @property
    def identificador(self) -> str:
        """Retorna el identificador único de la entidad."""
        return self._identificador

    def obtener_detalles(self) -> str:
        """Método abstracto que debe ser sobrescrito por las subclases."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")


# 4. Clase Cliente con encapsulación y validaciones estrictas
class Cliente(EntidadBase):
    """Representa un cliente de Software FJ con datos personales validados."""

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        """Retorna el nombre completo del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        # Valida que el nombre tenga al menos 2 caracteres
        if not valor or len(valor.strip()) < 2:
            logging.error(f"Intento de registrar nombre inválido: '{valor}'")
            raise ValueError("El nombre del cliente debe tener al menos 2 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        """Retorna el correo electrónico del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        # Valida formato básico de correo electrónico
        if not valor or "@" not in valor or "." not in valor.split("@")[-1]:
            logging.error(f"Intento de registrar correo inválido: '{valor}'")
            raise ValueError("El correo electrónico no es válido.")
        self._correo = valor.strip()

    @property
    def telefono(self) -> str:
        """Retorna el número de teléfono del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        # Valida que el teléfono contenga solo dígitos y tenga mínimo 7 caracteres
        if not valor or not valor.isdigit() or len(valor) < 7:
            logging.error(f"Intento de registrar teléfono inválido: '{valor}'")
            raise ValueError("El teléfono debe contener solo números y al menos 7 dígitos.")
        self._telefono = valor

    def obtener_detalles(self) -> str:
        """Retorna la información resumida del cliente."""
        return (
            f"Cliente [ID: {self.identificador}] - Nombre: {self.nombre}, "
            f"Correo: {self.correo}, Teléfono: {self.telefono}"
        )


# 5. Clase abstracta Servicio y clases derivadas (polimorfismo y sobrecarga con parámetros)
class Servicio(EntidadBase):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, disponible: bool = True):
        super().__init__(identificador)
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base
        self.disponible = disponible

    @property
    def costo_base(self) -> float:
        """Retorna el costo base del servicio."""
        return self._costo_base

    @costo_base.setter
    def costo_base(self, valor: float):
        # Valida que el costo base sea positivo
        if valor <= 0:
            logging.error(f"Intento de asignar costo base inválido ({valor}) al servicio {self.identificador}")
            raise ValueError("El costo base debe ser mayor que cero.")
        self._costo_base = float(valor)

    def validar_parametros(self) -> bool:
        """Valida que el servicio esté disponible para su contratación."""
        if not self.disponible:
            raise ServicioNoDisponibleException(
                f"El servicio '{self.nombre_servicio}' no se encuentra disponible."
            )
        return True

    def calcular_costo(self, *args, **kwargs) -> float:
        """Método polimórfico para calcular el costo del servicio."""
        raise NotImplementedError("Las subclases deben implementar calcular_costo.")

    def obtener_detalles(self) -> str:
        """Retorna la descripción general del servicio."""
        estado = "Disponible" if self.disponible else "No disponible"
        return f"Servicio [{self.identificador}] {self.nombre_servicio} - Base: ${self.costo_base:.2f} ({estado})"


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas."""

    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, capacidad: int, disponible: bool = True):
        super().__init__(identificador, nombre_servicio, costo_base, disponible)
        if capacidad <= 0:
            raise ValueError("La capacidad de la sala debe ser mayor que cero.")
        self.capacidad = capacidad

    # Simula sobrecarga mediante parámetros opcionales para descuento e impuesto
    def calcular_costo(self, descuento: float = 0.0, impuesto: float = 0.19) -> float:
        """Calcula el costo de la sala aplicando descuento opcional e impuesto."""
        try:
            self.validar_parametros()
            if not (0.0 <= descuento < 1.0):
                raise ValueError("El descuento debe estar entre 0.0 y menor a 1.0.")
            if impuesto < 0.0:
                raise ValueError("El impuesto no puede ser negativo.")
            subtotal = self.costo_base * (1 - descuento)
            total = subtotal * (1 + impuesto)
            return round(total, 2)
        except Exception as exc:
            logging.error(f"Error al calcular costo en ReservaSala ({self.identificador}): {exc}")
            raise ServicioNoDisponibleException("No fue posible calcular el costo de la sala.") from exc

    def obtener_detalles(self) -> str:
        """Sobrescribe detalles incluyendo la capacidad de la sala."""
        return f"{super().obtener_detalles()} - Capacidad: {self.capacidad} personas"


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos."""

    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, serial_equipo: str, disponible: bool = True):
        super().__init__(identificador, nombre_servicio, costo_base, disponible)
        if not serial_equipo or not serial_equipo.strip():
            raise ValueError("El serial del equipo es obligatorio.")
        self.serial_equipo = serial_equipo.strip()

    # Simula sobrecarga mediante parámetros opcionales de horas y descuento
    def calcular_costo(self, horas: int = 1, descuento: float = 0.0) -> float:
        """Calcula el costo del alquiler según número de horas y descuento opcional."""
        try:
            self.validar_parametros()
            if horas <= 0:
                raise ValueError("Las horas de alquiler deben ser mayores a cero.")
            if not (0.0 <= descuento < 1.0):
                raise ValueError("El descuento debe estar entre 0.0 y menor a 1.0.")
            total = (self.costo_base * horas) * (1 - descuento)
            return round(total, 2)
        except Exception as exc:
            logging.error(f"Error al calcular costo en AlquilerEquipo ({self.identificador}): {exc}")
            raise ServicioNoDisponibleException("Error al calcular el costo del alquiler de equipo.") from exc

    def obtener_detalles(self) -> str:
        """Sobrescribe detalles incluyendo el serial del equipo."""
        return f"{super().obtener_detalles()} - Serial: {self.serial_equipo}"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o estratégicas."""

    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, especialidad: str, disponible: bool = True):
        super().__init__(identificador, nombre_servicio, costo_base, disponible)
        if not especialidad or not especialidad.strip():
            raise ValueError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()

    # Simula sobrecarga mediante nivel de complejidad y horas opcionales
    def calcular_costo(self, nivel_complejidad: int = 1, horas: int = 1) -> float:
        """Calcula el costo de la asesoría según nivel de complejidad (1-3) y horas."""
        try:
            self.validar_parametros()
            if nivel_complejidad not in (1, 2, 3):
                raise ValueError("El nivel de complejidad debe ser 1, 2 o 3.")
            if horas <= 0:
                raise ValueError("Las horas de asesoría deben ser mayores a cero.")
            total = self.costo_base * nivel_complejidad * horas
            return round(total, 2)
        except Exception as exc:
            logging.error(f"Error al calcular costo en AsesoriaEspecializada ({self.identificador}): {exc}")
            raise ServicioNoDisponibleException("Error al calcular el costo de la asesoría.") from exc

    def obtener_detalles(self) -> str:
        """Sobrescribe detalles incluyendo la especialidad."""
        return f"{super().obtener_detalles()} - Especialidad: {self.especialidad}"


# 6. Clase Reserva que integra cliente, servicio, duración y estado
class Reserva:
    """Gestiona el ciclo de vida de una reserva dentro del sistema."""

    contador_reservas = 1000

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: int, fecha_inicio: str | None = None):
        Reserva.contador_reservas += 1
        self.codigo_reserva = f"RES-{Reserva.contador_reservas}"
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.fecha_inicio = fecha_inicio or datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.estado = "Creada"

    def confirmar_reserva(self, costo_estimado: float | None = None):
        """Confirma la reserva usando bloques try/except/else/finally y encadenamiento."""
        try:
            # Valida que exista cliente y servicio asociados
            if not isinstance(self.cliente, Cliente):
                raise ClienteNoEncontradoException("La reserva no tiene un cliente válido asignado.")
            if not isinstance(self.servicio, Servicio):
                raise ServicioNoDisponibleException("La reserva no tiene un servicio válido asignado.")
            self.servicio.validar_parametros()

            # Valida duración positiva
            if self.duracion <= 0:
                raise ValueError("La duración de la reserva debe ser mayor a cero.")
        except Exception as exc:
            self.estado = "Fallida"
            logging.error(f"Error al confirmar reserva {self.codigo_reserva}: {exc}")
            # Encadena la excepción original dentro de ReservaInvalidaException
            raise ReservaInvalidaException(
                f"No se pudo confirmar la reserva {self.codigo_reserva}."
            ) from exc
        else:
            # Se ejecuta solo si no hubo excepciones en el bloque try
            self.estado = "Confirmada"
            detalle_costo = f" | Costo: ${costo_estimado:.2f}" if costo_estimado is not None else ""
            logging.info(f"Reserva {self.codigo_reserva} confirmada para {self.cliente.nombre}{detalle_costo}.")
            print(f"   -> [ÉXITO] Reserva {self.codigo_reserva} confirmada para {self.cliente.nombre}{detalle_costo}.")
        finally:
            # Se ejecuta siempre para dejar trazabilidad del estado
            print(f"   [ESTADO] {self.codigo_reserva} -> {self.estado}")

    def cancelar_reserva(self):
        """Cancela una reserva y registra el evento en el log."""
        self.estado = "Cancelada"
        logging.info(f"Reserva {self.codigo_reserva} cancelada por solicitud.")
        print(f"   -> [AVISO] Reserva {self.codigo_reserva} marcada como Cancelada.")


# 7. Simulación de 10 operaciones completas (válidas e inválidas) sin base de datos
def ejecutar_simulacion():
    """Ejecuta 10 operaciones para validar estabilidad, POO y manejo de excepciones."""
    print("=== INICIANDO SIMULACIÓN DE 10 OPERACIONES - SOFTWARE FJ ===\n")
    clientes: list[Cliente] = []
    servicios: list[Servicio] = []
    reservas: list[Reserva] = []

    # Operación 1: Registro válido de cliente
    print("Op 1: Registro válido de cliente...")
    try:
        c1 = Cliente("C01", "María Blanco", "maria.blanco@unad.edu.co", "3506271896")
        clientes.append(c1)
        logging.info(f"Cliente registrado: {c1.obtener_detalles()}")
        print(f"   Registrado: {c1.obtener_detalles()}\n")
    except Exception as e:
        print(f"   Error inesperado en Op 1: {e}\n")

    # Operación 2: Registro inválido de cliente (correo sin '@')
    print("Op 2: Intento de registro de cliente con correo inválido...")
    try:
        c_invalido = Cliente("C02", "Carlos Ruiz", "carlosruiz.correo.com", "3112233445")
        clientes.append(c_invalido)
    except ValueError as e:
        print(f"   [Controlado] Error de validación: {e}\n")

    # Operación 3: Creación válida de servicio de reserva de sala y cálculo de costo
    print("Op 3: Creación de servicio ReservaSala y cálculo de costo con descuento...")
    try:
        s1 = ReservaSala("S01", "Sala de Conferencias A", 80000.0, capacidad=15)
        servicios.append(s1)
        costo_s1 = s1.calcular_costo(descuento=0.15)
        print(f"   Creado: {s1.obtener_detalles()} | Total con 15% desc + IVA: ${costo_s1}\n")
    except Exception as e:
        print(f"   [Controlado] {e}\n")

    # Operación 4: Creación válida de servicio de alquiler de equipo
    print("Op 4: Creación de servicio AlquilerEquipo...")
    try:
        s2 = AlquilerEquipo("S02", "Laptop Ingeniería i7", 25000.0, "EQ-LAP-2026")
        servicios.append(s2)
        costo_s2 = s2.calcular_costo(horas=3)
        print(f"   Creado: {s2.obtener_detalles()} | Total 3h: ${costo_s2}\n")
    except Exception as e:
        print(f"   [Controlado] {e}\n")

    # Operación 5: Creación válida de servicio de asesoría especializada
    print("Op 5: Creación de servicio AsesoriaEspecializada...")
    try:
        s3 = AsesoriaEspecializada("S03", "Arquitectura POO y Excepciones", 90000.0, "Ingeniería de Software")
        servicios.append(s3)
        costo_s3 = s3.calcular_costo(nivel_complejidad=2, horas=2)
        print(f"   Creado: {s3.obtener_detalles()} | Total nivel 2 (2h): ${costo_s3}\n")
    except Exception as e:
        print(f"   [Controlado] {e}\n")

    # Operación 6: Reserva exitosa
    print("Op 6: Creación y confirmación de reserva exitosa...")
    try:
        r1 = Reserva(clientes[0], servicios[0], duracion=2)
        r1.confirmar_reserva(costo_estimado=servicios[0].calcular_costo(descuento=0.10))
        reservas.append(r1)
        print("")
    except ReservaInvalidaException as e:
        print(f"   [Controlado] {e} | Causa: {e.__cause__}\n")

    # Operación 7: Intento de reserva fallida por duración inválida (con encadenamiento)
    print("Op 7: Intento de reserva con duración inválida (-4 horas)...")
    try:
        r2 = Reserva(clientes[0], servicios[1], duracion=-4)
        r2.confirmar_reserva()
        reservas.append(r2)
    except ReservaInvalidaException as e:
        print(f"   [Controlado] {e} | Causa raíz: {e.__cause__}\n")

    # Operación 8: Cálculo de costo inválido por nivel de complejidad fuera de rango
    print("Op 8: Intento de cálculo de costo con nivel de complejidad inválido (5)...")
    try:
        servicios[2].calcular_costo(nivel_complejidad=5)
    except ServicioNoDisponibleException as e:
        print(f"   [Controlado] {e} | Causa raíz: {e.__cause__}\n")

    # Operación 9: Cancelación de la reserva confirmada en Op 6
    print("Op 9: Cancelación de reserva existente...")
    try:
        if reservas:
            reservas[0].cancelar_reserva()
        print("")
    except Exception as e:
        print(f"   [Controlado] {e}\n")

    # Operación 10: Registro de un segundo cliente válido y cierre de simulación
    print("Op 10: Registro de segundo cliente válido y verificación final...")
    try:
        c2 = Cliente("C03", "Sofía Mendoza", "sofia.mendoza@correo.com", "3159876543")
        clientes.append(c2)
        logging.info(f"Cliente registrado: {c2.obtener_detalles()}")
        print(f"   Registrado: {c2.obtener_detalles()}")
        print("\n=== SIMULACIÓN COMPLETADA SIN INTERRUPCIONES ===")
    except Exception as e:
        print(f"   [Controlado] {e}")
    finally:
        print("   [LOG] Revisa 'sistema_errores.log' para ver el historial completo de eventos y errores.")


if __name__ == "__main__":
    ejecutar_simulacion()