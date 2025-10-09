// 1. DATOS INICIALES (PARA CARGAR SI LOCALSTORAGE ESTÁ VACÍO)

const INICIAL_SOLICITUDES_DATA = [
    {
        "id": 101,
        "empresa": "FinanzasRápidas",
        "estado": "PENDIENTE",
        "razonSocial": "Comercializadora S.A.",
        "formaJuridica": "Sociedad Anónima",
        "email": "contacto@comercializadora.com",
        "cuit": "30-71234567-8",
        "actividadPrincipal": "Comercio al por mayor",
        "telefono": "54-11-4567-8900",
        "calleYNumero": "Av. Libertador 1234",
        "pisoDpto": "Piso 5",
        "provincia": "Buenos Aires",
        "ciudadLocalidad": "CABA",
        "codigoPostal": "1425",
        "fechaCierreEjercicio": "31/12",
        "activoTotal": 55000000.00,
        "ventasNetasAnuales": 98000000.00,
        "cantEmpleados": 45
    },
    {
        "id": 102,
        "empresa": "CréditoTotal",
        "estado": "PENDIENTE",
        "razonSocial": "Servicios Digitales SRL",
        "formaJuridica": "Sociedad de Responsabilidad Limitada",
        "email": "info@serviciosdigitales.net",
        "cuit": "20-98765432-1",
        "actividadPrincipal": "Desarrollo de Software",
        "telefono": "54-351-2345-6789",
        "calleYNumero": "Ruta 20 Km 5",
        "pisoDpto": "Lote 12",
        "provincia": "Córdoba",
        "ciudadLocalidad": "Malagueño",
        "codigoPostal": "5101",
        "fechaCierreEjercicio": "30/06",
        "activoTotal": 12000000.00,
        "ventasNetasAnuales": 25000000.00,
        "cantEmpleados": 12
    },
    {
        "id": 103,
        "empresa": "FinanzasRápidas",
        "estado": "APROBADO",
        "razonSocial": "Otra Comercializadora",
        "formaJuridica": "S.A.",
        "email": "info@otra.com",
        "cuit": "25-11223344-5",
        "actividadPrincipal": "Venta minorista",
        "telefono": "54-11-9988-7766",
        "calleYNumero": "Calle Falsa 123",
        "pisoDpto": "Oficina 1",
        "provincia": "Santa Fe",
        "ciudadLocalidad": "Rosario",
        "codigoPostal": "2000",
        "fechaCierreEjercicio": "30/11",
        "activoTotal": 8000000.00,
        "ventasNetasAnuales": 18000000.00,
        "cantEmpleados": 10
    },
        {
        "id": 104,
        "empresa": "ComeChingolo",
        "estado": "PENDIENTE",
        "razonSocial": "Otra Comercializadora",
        "formaJuridica": "S.A.",
        "email": "info@otra.com",
        "cuit": "25-11223344-5",
        "actividadPrincipal": "Venta minorista",
        "telefono": "54-11-9988-7766",
        "calleYNumero": "Calle Falsa 123",
        "pisoDpto": "Oficina 1",
        "provincia": "Santa Fe",
        "ciudadLocalidad": "Rosario",
        "codigoPostal": "2000",
        "fechaCierreEjercicio": "30/11",
        "activoTotal": 8000000.00,
        "ventasNetasAnuales": 18000000.00,
        "cantEmpleados": 10
    }
];

const STORAGE_KEY = 'solicitudesPrestamo';
let companieActive = null; 


//FUNCIONES DE UTILIDAD PARA LOCALSTORAGE

function getSolicitudes() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
}

function saveSolicitudes(solicitudes) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(solicitudes));
}

// 3. LÓGICA DE NAVEGACIÓN POR EMPRESA

function updateActiveItem(clickedItem) {
    const listCompanies = document.getElementById('listCompanies');
    if (!listCompanies) return;

    listCompanies.querySelectorAll('.companieItem').forEach(item => {
        item.classList.remove('active');
    });
    if (clickedItem) {
        clickedItem.classList.add('active');
    }
}

function setuplistCompanies() {
    const listCompanies = document.getElementById('listCompanies');
    const allRequests = getSolicitudes();
    
    const companies = [...new Set(allRequests.map(sol => sol.empresa))].sort();
    listCompanies.innerHTML = ''; 

    if (companies.length === 0) {
        listCompanies.innerHTML = '<div class="companieItem">No hay datos.</div>';
        return;
    }

    companies.forEach(empresa => {
        const item = document.createElement('div');
        item.className = 'companieItem';
        item.textContent = empresa;
        item.dataset.empresa = empresa; 

        item.addEventListener('click', (event) => {
            companieActive = empresa;
            renderDashboard();
            updateActiveItem(event.target);
        });
        listCompanies.appendChild(item);
    });
}


//FUNCIONES PRINCIPALES DEL DASHBOARD


function renderDashboard() {
    const dashboardContainer = document.getElementById('dashboardContainer');
    const noDataMessage = document.getElementById('noDataMessage');
    const empresaActualNombre = document.getElementById('empresa-actual-nombre');
    
    const allRequests = getSolicitudes(); 
    dashboardContainer.innerHTML = ''; 

    const solicitudesFiltradas = allRequests.filter(solicitud => 
        solicitud.empresa === companieActive
    );
    
    empresaActualNombre.textContent = companieActive || "Sin Empresa Seleccionada";

    if (!companieActive || solicitudesFiltradas.length === 0) {
        noDataMessage.textContent = companieActive ? 
            `No hay solicitudes para ${companieActive}.` :
            'Seleccione una empresa en el menú lateral.';
        noDataMessage.classList.remove('hidden');
        noDataMessage.classList.add('messageInfo');
        return;
    }

    noDataMessage.classList.add('hidden');

    solicitudesFiltradas.forEach(solicitud => {
        const card = document.createElement('div');
        card.className = 'applicationCard';
        card.dataset.id = solicitud.id; 

        let statusClass = '';
        if (solicitud.estado === 'APROBADO') {
            statusClass = 'statusApproved';
        } else if (solicitud.estado === 'RECHAZADO') {
            statusClass = 'statusRejected';
        } else {
            statusClass = 'statusEarring';
        }

        const formatCurrency = (amount) => amount.toLocaleString('es-AR', { minimumFractionDigits: 2 });


        card.innerHTML = `
            <h3>Solicitud #${solicitud.id} - ${solicitud.razonSocial}</h3>
            
            <div class="infoContainer">
                <div>
                    <p>Razon Social: <b>${solicitud.razonSocial}</b></p>
                    <p>Forma Jurídica: ${solicitud.formaJuridica}</p>
                    <p>Email: ${solicitud.email}</p>
                </div>

                <div>
                    <p>C.U.I.T: ${solicitud.cuit}</p>
                    <p>Actividad Principal: ${solicitud.actividadPrincipal}</p>
                    <p>N° Telefono: ${solicitud.telefono}</p>
                </div>
            </div>

            <div class="infoContainer">
                <div>
                    <p>Calle y Número: ${solicitud.calleYNumero}</p>
                    <p>Provincia: ${solicitud.provincia}</p>
                    <p>Código Postal: ${solicitud.codigoPostal}</p>
                </div>

                <div>
                    <p>Piso/Dpto: ${solicitud.pisoDpto}</p>
                    <p>Ciudad/Localidad: ${solicitud.ciudadLocalidad}</p>
                </div>
            </div>

            <div class="infoContainer">
                <div>
                    <p>Fecha Cierre de Ejercicio: ${solicitud.fechaCierreEjercicio}</p>
                    <p>Activo Total ($): <b>${formatCurrency(solicitud.activoTotal)}</b></p>
                </div>

                <div>
                    <p>Ventas Netas Anuales ($): <b>${formatCurrency(solicitud.ventasNetasAnuales)}</b></p>
                    <p>Cant. de Empleados: ${solicitud.cantEmpleados}</p>
                </div>
            </div>
            <div class="actions">
                <div>
                    <button class="approve" data-action="APROBADO" ${solicitud.estado !== 'PENDIENTE' ? 'disabled' : ''}>Aprobar</button>
                    <button class="decline" data-action="RECHAZADO" ${solicitud.estado !== 'PENDIENTE' ? 'disabled' : ''}>Rechazar</button>
                </div>

                <span class="applicationStatus ${statusClass}">${solicitud.estado}</span>
            </div>
        `;
        dashboardContainer.appendChild(card);
    });

    addActionListener();
}

function addActionListener() {
    const dashboardContainer = document.getElementById('dashboardContainer');
    dashboardContainer.querySelectorAll('.actions button').forEach(button => {
        button.addEventListener('click', (event) => {
            const card = event.target.closest('.applicationCard');
            const id = parseInt(card.dataset.id);
            const nuevoEstado = event.target.dataset.action; 

            updateSolicitudStatus(id, nuevoEstado);
        });
    });
}

function updateSolicitudStatus(id, nuevoEstado) {
    let solicitudes = getSolicitudes();
    const index = solicitudes.findIndex(sol => sol.id === id);

    if (index !== -1) {
        solicitudes[index].estado = nuevoEstado;
        
        saveSolicitudes(solicitudes);
        
        renderDashboard();
        alert(`Solicitud #${id} marcada como: ${nuevoEstado}`);
    }
}


//FUNCION PARA QUE EL DASHBOARD SE VEA SOLO SI SE INICIO SESIÓN


document.addEventListener('DOMContentLoaded', () => {
    if (!localStorage.getItem(STORAGE_KEY)) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(INICIAL_SOLICITUDES_DATA));
        console.log("LocalStorage vacío. Se cargaron datos de prueba.");
    }
    
    setuplistCompanies();
    
    if (!companieActive) {
        renderDashboard();
    }
});


    const dbName = 'creditbusters_users_db';


    function load() {
        const usersJson = localStorage.getItem(this.dbName);
        return usersJson ? JSON.parse(usersJson) : [];
    }

    function setupDashboardPage() {
        const loggedInUser = JSON.parse(localStorage.getItem('loggedInUser'));
        if (!loggedInUser) {
            window.location.href = 'log-in.html';
            return;
        }

        const welcomeEl = document.getElementById('welcomeMessage');
        if (welcomeEl) {
            welcomeEl.textContent = `Hola, ${loggedInUser.name}`;
        }

        const userInfoEl = document.getElementById('userInfo');
        if (userInfoEl) {
            const logoutBtn = document.createElement('button');
            logoutBtn.textContent = 'Cerrar Sesión';
            logoutBtn.className = 'btn btnSecondary';
            logoutBtn.onclick = () => {
                localStorage.removeItem('loggedInUser');
                this._setFlashMessage('Has cerrado sesión.', 'success');
                window.location.href = 'log-in.html';
            };
            userInfoEl.appendChild(logoutBtn);
        }

        load()
    };

    setupDashboardPage();

