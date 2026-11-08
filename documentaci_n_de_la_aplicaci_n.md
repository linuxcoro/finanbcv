# 📱 FinanBCV - Gestor de Ventas Financiadas a Tasa BCV

**FinanBCV** es una aplicación web progresiva y liviana (Single-Page Application) diseñada para comerciantes que venden productos en dólares y permiten financiamiento por cuotas calculadas a la tasa oficial del Banco Central de Venezuela (BCV). 

La aplicación permite llevar el control de abonos de clientes, calcular desgloses de iniciales y cuotas en tiempo real, y generar comprobantes de Pago Móvil listos para compartir por WhatsApp o cualquier app de mensajería nativa.

---

## 🚀 Características Principales

* **Cálculo Automático a Tasa BCV:** Convierte el monto en dólares a bolívares según la tasa ingresada, descuenta la inicial (%) y divide el saldo exacto en las cuotas acordadas.
* **Integración Nativa de Pago Móvil:** Configura tus datos bancarios una sola vez (Banco, Cédula/RIF y Teléfono) y genera plantillas de cobro personalizadas con 1 clic.
* **Compartir Directo (Web Share API):** Envía la salida del Pago Móvil con el desglose de partes restantes directamente a WhatsApp, Telegram o SMS usando el menú nativo del dispositivo.
* **Modo Oscuro / Claro:** Alternador de interfaz de usuario con almacenamiento persistente en el navegador para ahorrar batería en pantallas OLED.
* **Persistencia Local (`localStorage`):** Guarda la lista de clientes, abonos y configuraciones directamente en el almacenamiento del dispositivo, sin requerir internet ni bases de datos externas.
* **Diseño Responsive / Mobile-First:** Interfaz moderna adaptada para teléfonos celulares y computadoras con Tailwind CSS.

---

## 🛠️ Arquitectura y Tecnologías Utilizadas

La aplicación está construida sobre una arquitectura limpia de **un solo archivo (Single-File App)** para garantizar rapidez de carga y facilidad de empaquetado en APK:

* **HTML5:** Estructura semántica de la aplicación y modales interactivos.
* **Tailwind CSS (CDN):** Framework de utilidades CSS para el diseño responsive, soporte de modo oscuro por clases (`dark:`) y componentes visuales elegantes.
* **JavaScript (Vanilla ES6+):** 
  * Manejo del Estado (Clientes, Pagos, Ajustes).
  * `localStorage` para almacenamiento persistente.
  * API Nativa `navigator.share` y `document.execCommand('copy')` para salida de mensajes.
  * Manipulación dinámica del DOM y lógica de cálculo financiero.
* **Lucide Icons:** Iconografía liviana vectorial.

---

## 📋 Estructura de Datos (JSON Schema Interno)

### Objeto Crédito (`credits`)
```json
{
  "id": 1700000000000,
  "clientName": "Juan Pérez (0412-1112233)",
  "totalUsd": 100.00,
  "bcvRate": 36.50,
  "initialPercent": 30,
  "totalInstallments": 3,
  "remainingInstallments": 2,
  "installmentUsd": 23.33,
  "createdAt": "8/11/2026"
}
```

### Objeto Ajustes Pago Móvil (`settings`)
```json
{
  "bank": "Banesco (0134)",
  "id": "V-12345678",
  "phone": "0414-1234567"
}
```

---

## ⚙️ Guía de Uso del Sistema

1. **Configuración Inicial:**
   * Haz clic en el icono del código QR / Ajustes en la barra superior.
   * Ingresa tu Banco, Cédula/RIF y número de teléfono de Pago Móvil.
2. **Registrar Venta:**
   * Introduce el nombre y teléfono del cliente.
   * Ingresa el total en USD y la tasa BCV del día.
   * Define el porcentaje de inicial y el número de partes.
   * Presiona **"Registrar Crédito"**.
3. **Abonar y Compartir:**
   * Cuando el cliente realice un pago, presiona **"Abonar Cuota"** en su tarjeta.
   * El sistema descontará una parte restante y abrirá el modal de salida.
   * Presiona **"Compartir App"** para enviarlo directamente por WhatsApp.

---

## 📦 Instrucciones para Compilar como Aplicación Móvil (APK)

Para convertir este proyecto web en un instalable `.apk` para Android:

1. Crea un repositorio en GitHub con el nombre `finanbcv`.
2. Sube este código en la raíz con el nombre `index.html`.
3. Notifica en el chat para obtener el workflow listo de **GitHub Actions** (`.github/workflows/build-apk.yml`) que compilará el instalable automáticamente sin instalar programas en tu computadora.