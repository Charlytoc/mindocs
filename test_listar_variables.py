from docxtpl import DocxTemplate, RichText

context = {
    "detalle_bienes_inmuebles": "Casa en Av. Reforma 123, CDMX",
    "detalle_hijos": "María Pérez (10 años), José Pérez (8 años)",
    "detalles_abogados": "LIC. MARÍA LÓPEZ (Cédula: 1234567), LIC. JUAN RAMÍREZ (Cédula: 2345678)",
    "domicilio_conyugal": "Av. Principal 456, Toluca",
    "domicilio_del_demandado": "Calle Secundaria 789, Toluca",
    "domicilio_del_promovente": "Calle Falsa 123, Toluca",
    "fecha_de_cuidado": "01 de enero de 2020",
    "fecha_matrimonio": "15 de febrero de 2010",
    "nombre_completo_del_demandado": "LAURA MARTÍNEZ",
    "nombre_del_promovente": "JUAN PÉREZ",
    "nombre_promovente": "JUAN PÉREZ",
    "persona_abogada_acceso_al_sistema": "LIC. CARLOS SÁNCHEZ (Cédula: 4567890, Correo: carlos@abogados.com)",
    "persona_autorizada_notificaciones": "PEDRO GÓMEZ",
    "tipo_regimen_conyugal": "sociedad conyugal"
}

doc = DocxTemplate("machote_di.docx")
doc.render(context)
doc.save("machote_di_prueba.docx")
print("Documento de prueba generado: machote_di_prueba.docx")
