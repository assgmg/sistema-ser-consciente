if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = carregar_equipamentos_iniciais()

if "historico" not in st.session_state:
    historico_convertido = []
    for h in carregar_dados_disco():
        if not isinstance(h, dict):
            continue
        h_conv = h.copy()
        h_conv["fotos_antes_bytes"] = normalizar_lista_fotos(
            h_conv, "fotos_antes_bytes", "foto_antes_bytes"
        )
        h_conv["fotos_depois_bytes"] = normalizar_lista_fotos(
            h_conv, "fotos_depois_bytes", "foto_depois_bytes"
        )
        h_conv.pop("foto_antes_bytes", None)
        h_conv.pop("foto_depois_bytes", None)
        historico_convertido.append(h_conv)
    st.session_state.historico = historico_convertido

try:
    tag_url = st.query_params.get("tag", None)
except Exception:
    tag_url = None

tag_qr_lido = tag_url.strip().upper() if tag_url else None

if "qr_liberado_tags" not in st.session_state:
    st.session_state.qr_liberado_tags = []


def exibir_fotos_registro(h):
    fotos_antes = h.get("fotos_antes_bytes") or normalizar_lista_fotos(
        h, "fotos_antes_bytes", "foto_antes"
    )
    fotos_depois = h.get("fotos_depois_bytes") or normalizar_lista_fotos(
        h, "fotos_depois_bytes", "foto_depois"
    )

    if fotos_antes or fotos_depois:
        col1, col2 = st.columns(2)
        with col1:
            if fotos_antes:
                st.markdown("**📷 Fotos ANTES:**")
                for i, img_data in enumerate(fotos_antes):
                    try:
                        st.image(
                            img_data,
                            caption="Antes #"
                            + str(i + 1)
                            + " - "
                            + str(h.get("data", "")),
                            width="stretch",
                        )
                    except Exception:
                        st.warning(f"Não foi possível exibir a foto ANTES #{i + 1}.")
        with col2:
            if fotos_depois:
                st.markdown("**📷 Fotos DEPOIS:**")
                for i, img_data in enumerate(fotos_depois):
                    try:
                        st.image(
                            img_data,
                            caption="Depois #"
                            + str(i + 1)
                            + " - "
                            + str(h.get("data", "")),
                            width="stretch",
                        )
                    except Exception:
                        st.warning(f"Não foi possível exibir a foto DEPOIS #{i + 1}.")


def renderizar_etiqueta_html(eq_sel):
    link_equip = BASE_URL + "/?tag=" + eq_sel["tag"]
    api_qr_url = (
        "https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=" + link_equip
    )
    return (
        '<div class="etiqueta-box">'
        '<div class="etiqueta-header">PMOC - SER CONSCIENTE</div>'
        '<div style="font-size: 8px; line-height: 1.1;">'
        "<b>TAG:</b> " + escapar_xml(eq_sel["tag"]) + "<br>"
        "<b>Amb:</b> " + escapar_xml(eq_sel["ambiente"]) + "<br>"
        "<b>Equip:</b> "
        + escapar_xml(formatar_equipamento_com_serie(eq_sel))
        + "<br>"
        "<b>Carga:</b> " + escapar_xml(eq_sel["btus"]) + " BTUs</div>"
        '<div style="text-align: center; margin: 1px 0;">'
        '<img src="'
        + escapar_xml(api_qr_url)
        + '" width="65" height="65" style="border: 1px solid #ddd; padding: 1px; background: #fff;"></div>'
        '<div style="text-align: center; font-size: 6px; color: #000; font-weight: bold; line-height: 1;">'
        "Eng. Alessandro Coelho (CREA-MG 238468-D)<br>ART: MG20265436050</div></div>"
    )


def adicionar_bloco_fotos_pdf(story, titulo_bloco, lista_bytes, estilo_check, style_imgs):
    if not lista_bytes:
        return
    story.append(Paragraph(titulo_bloco, estilo_check))
    linha_imgs = []
    for item_img in lista_bytes:
        try:
            bytes_dec = decodificar_foto_segura(item_img)
            jpeg_limpo = converter_bytes_para_jpeg_seguro(bytes_dec)
            if jpeg_limpo:
                linha_imgs.append(
                    RLImage(io.BytesIO(jpeg_limpo), width=4.0 * cm, height=3.0 * cm)
                )
                if len(linha_imgs) == 2:
                    t_imgs = Table([linha_imgs], colWidths=[4.5 * cm, 4.5 * cm])
                    t_imgs.setStyle(style_imgs)
                    story.append(Spacer(1, 3))
                    story.append(t_imgs)
                    linha_imgs = []
        except Exception:
            pass
    if linha_imgs:
        while len(linha_imgs) < 2:
            linha_imgs.append("")
        t_imgs = Table([linha_imgs], colWidths=[4.5 * cm, 4.5 * cm])
        t_imgs.setStyle(style_imgs)
        story.append(Spacer(1, 3))
        story.append(t_imgs)


def montar_etiqueta_pdf(
    eq_obj, estilo_header, estilo_texto, estilo_footer, style_hdr, style_etq
):
    link_eq = BASE_URL + "/?tag=" + str(eq_obj["tag"])
    qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + link_eq
    qr_img_obj = None
    try:
        qr_bytes = urllib.request.urlopen(qr_url, timeout=3).read()
        qr_jpeg = converter_bytes_para_jpeg_seguro(qr_bytes)
        if qr_jpeg:
            qr_img_obj = RLImage(io.BytesIO(qr_jpeg), width=1.6 * cm, height=1.6 * cm)
    except Exception:
        pass

    t_header = Table(
        [[Paragraph("<b>PMOC - SER CONSCIENTE</b>", estilo_header)]],
        colWidths=[4.6 * cm],
    )
    t_header.setStyle(style_hdr)

    txt_dados = Paragraph(
        "<b>TAG:</b> " + escapar_xml(eq_obj["tag"]) + "<br/>"
        + "<b>Amb:</b> " + escapar_xml(eq_obj["ambiente"]) + "<br/>"
        + "<b>Equip:</b> "
        + escapar_xml(formatar_equipamento_com_serie(eq_obj))
        + "<br/>"
        + "<b>Carga:</b> " + escapar_xml(eq_obj["btus"]) + " BTUs",
        estilo_texto,
    )
    txt_rodape = Paragraph(
        "Eng. Alessandro Coelho (CREA-MG 238468-D)<br/><b>ART:</b> MG20265436050",
        estilo_footer,
    )

    conteudo = [t_header, Spacer(1, 1), txt_dados, Spacer(1, 0.5)]
    if qr_img_obj:
        conteudo.append(qr_img_obj)
    conteudo.append(Spacer(1, 0.5))
    conteudo.append(txt_rodape)

    t_etiqueta = Table([[conteudo]], colWidths=[5.0 * cm], rowHeights=[5.0 * cm])
    t_etiqueta.setStyle(style_etq)
    return t_etiqueta


if logo_img is not None:
    try:
        st.sidebar.image(logo_img, width="stretch")
    except Exception:
        pass

st.sidebar.title("❄️ PMOC Digital")
st.sidebar.subheader("Instituto Ser Consciente Ltda")
st.sidebar.caption("Resp. Técnico: Eng. Alessandro Coelho (CREA-MG 238468-D)")
st.sidebar.caption("ART: MG20265436050")
st.sidebar.markdown("---")

if "senha_salva" not in st.session_state:
    st.session_state.senha_salva = ""

if st.session_state.senha_salva not in CREDENCIAIS_VALIDAS:
    st.sidebar.markdown("### 🔐 Acesso Restrito")
    senha_input = st.sidebar.text_input("Credencial de acesso:", type="password")
    if senha_input in CREDENCIAIS_VALIDAS:
        st.session_state.senha_salva = senha_input
        st.rerun()
    senha_input_ativo = senha_input
else:
    senha_input_ativo = st.session_state.senha_salva
    st.sidebar.success(
        "✅ Modo Administrador"
        if senha_input_ativo == SENHA_ADMIN
        else "👁️ Modo Fiscalização"
    )
    if st.sidebar.button("🚪 Sair / Desconectar"):
        st.session_state.senha_salva = ""
        st.session_state.qr_liberado_tags = []
        st.rerun()

st.sidebar.markdown("---")

eh_admin = senha_input_ativo == SENHA_ADMIN
eh_fiscal = senha_input_ativo == SENHA_VISA

if eh_admin:
    opcoes_menu = [
        "📋 Informações do Equipamento",
        "🛠️ Registrar Manutenção",
        "✏️ Editar Previstos",
        "🖨️ Etiquetas 5x5 cm (Individual)",
        "📑 Lote A4 para Gráfica (Guilhotina)",
        "📊 Dashboard Geral",
        "📄 Relatório Fiscal A4",
    ]
else:
    opcoes_menu = [
        "📋 Informações do Equipamento",
        "📊 Dashboard Geral",
    ]

if "menu_navegacao" not in st.session_state or st.session_state.menu_navegacao not in opcoes_menu:
    st.session_state.menu_navegacao = opcoes_menu[0]

opcao = st.sidebar.radio("Navegação", opcoes_menu, key="menu_navegacao")

if opcao == "📋 Informações do Equipamento":
    st.header("📋 Informações do Equipamento - PMOC Oficial")
    st.info("ℹ️ Projeto validado pela Vineyard Engenharia | ART CREA-MG nº MG20265436050")

    equip = None
    tag_codigo = ""

    if tag_qr_lido:
        tag_codigo = tag_qr_lido
        st.info("📱 QR Code lido — Equipamento: **" + tag_codigo + "**")
        equip = next(
            (e for e in st.session_state.equipamentos if e.get("tag") == tag_codigo),
            None,
        )
        if not equip:
            st.error("❌ Equipamento não encontrado para a TAG informada.")
    else:
        tags_lista = [
            e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos
        ]
        tag_selecionada = st.selectbox("Selecione a TAG do Equipamento:", tags_lista)
        tag_codigo = tag_selecionada.split(" - ")[0]
        equip = next(
            (e for e in st.session_state.equipamentos if e.get("tag") == tag_codigo),
            None,
        )
        if not equip:
            st.error("❌ Equipamento não encontrado para a TAG informada.")

    if equip:
        hists = [h for h in st.session_state.historico if h.get("tag") == tag_codigo]

        data_ult_str = "-"
        d_prox_str = "-"
        tipo_freq = ""
        prox_tipo_str = ""

        if equip["status"] == "Previsto":
            status_exibicao = "🟡 Previsto (Aguardando Instalação)"
        elif hists:
            data_ult_str, d_prox_str, d_prox_obj, tipo_freq, prox_tipo_str = (
                calcular_proxima_manutencao(hists)
            )
            if d_prox_obj is not None:
                if datetime.date.today() <= d_prox_obj:
                    status_exibicao = "🟢 Em dia"
                else:
                    status_exibicao = "🔴 Em atraso"
            else:
                status_exibicao = "🟢 Em dia"
        else:
            status_exibicao = "⚪ Sem registro"

        tag_ja_liberada = tag_codigo in st.session_state.qr_liberado_tags
        senha_digitada_ok = eh_admin or eh_fiscal or tag_ja_liberada

        if tag_qr_lido and not senha_digitada_ok:
            st.subheader("📍 " + equip["ambiente"] + " (" + equip["tag"] + ")")
            st.write("**Data da última manutenção:** " + data_ult_str)
            st.write(
                "**Data da próxima manutenção:** "
                + d_prox_str
                + (" — *" + prox_tipo_str + "*" if prox_tipo_str else "")
            )
            if "Em dia" in status_exibicao:
                st.success("**Status:** " + status_exibicao)
            elif "Em atraso" in status_exibicao:
                st.error("**Status:** " + status_exibicao)
            else:
                st.info("**Status:** " + status_exibicao)

            st.markdown("---")
            st.write("🔐 Digite a senha para ver a informação completa do equipamento:")
            with st.form("form_senha_qr_" + tag_codigo):
                senha_qr_input = st.text_input("Senha:", type="password")
                if st.form_submit_button("🔓 Ver Informação Completa"):
                    if senha_qr_input in CREDENCIAIS_VALIDAS:
                        st.session_state.senha_salva = senha_qr_input
                        if tag_codigo not in st.session_state.qr_liberado_tags:
                            st.session_state.qr_liberado_tags.append(tag_codigo)
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta.")
        else:
            area_txt = str(equip.get("area_m2") or "").strip()
            ocup_txt = str(equip.get("ocupantes_max") or "").strip()
            detalhes_amb = []
            if area_txt:
                detalhes_amb.append("**Área Climatizada:** " + area_txt + " m²")
            if ocup_txt:
                detalhes_amb.append("**Ocupantes Máx.:** " + ocup_txt)

            st.subheader("📍 " + equip["ambiente"] + " (" + equip["tag"] + ")")
            st.write(
                "**Equipamento:** "
                + formatar_equipamento_com_serie(equip)
                + " | **Carga Térmica:** "
                + str(equip["btus"])
                + " BTUs"
            )
            if detalhes_amb:
                st.write(" | ".join(detalhes_amb))
            st.write("**Status de Instalação:** `" + equip["status"] + "`")
            st.write(
                "**Data da última manutenção:** "
                + data_ult_str
                + (" — *" + rotulo_ciclo_curto(tipo_freq) + "*" if tipo_freq else "")
            )
            st.write(
                "**Data da próxima manutenção:** "
                + d_prox_str
                + (" — *" + prox_tipo_str + "*" if prox_tipo_str else "")
            )

            if "Em dia" in status_exibicao:
                st.success("**Status:** " + status_exibicao)
            elif "Em atraso" in status_exibicao:
                st.error("**Status:** " + status_exibicao)
            else:
                st.info("**Status:** " + status_exibicao)

            if hists and equip["status"] != "Previsto":
                st.write("**Técnico Executor:** " + str(hists[-1].get("tecnico", "")))
                if hists[-1].get("visto"):
                    st.write("**Visto / Validação:** " + str(hists[-1].get("visto", "")))

            st.markdown("---")
            st.subheader("📋 Histórico Acumulado e Gerenciamento de Registros")

            if hists:
                for idx, h in enumerate(reversed(hists)):
                    indice_real = st.session_state.historico.index(h)
                    freq_reg = h.get("periodicidade", "Semestral")
                    num_manut = str(len(hists) - idx)
                    titulo_manut = (
                        "#### Manutenção #"
                        + num_manut
                        + " — Data: "
                        + str(h.get("data", ""))
                        + " ("
                        + freq_reg
                        + ")"
                    )
                    st.markdown(titulo_manut)
                    st.write("**Técnico Executor:** " + str(h.get("tecnico", "")))
                    if h.get("visto"):
                        st.write("**Visto / Validação:** " + str(h.get("visto", "")))

                    if h.get("checklist"):
                        st.write("**Itens Verificados (PMOC - Itens 4.1 a 4.18):**")
                        for item_nome, status_val in h["checklist"].items():
                            st.write(
                                "- "
                                + ("✅" if status_val else "❌")
                                + " "
                                + str(item_nome)
                            )

                    if h.get("obs"):
                        st.write("**Observações / Ocorrências:** " + str(h["obs"]))

                    exibir_fotos_registro(h)

                    if eh_admin:
                        with st.expander(
                            "✏️ Editar este Registro de Manutenção (#"
                            + num_manut
                            + " — "
                            + str(h.get("data", ""))
                            + ")"
                        ):
                            reg_atual = st.session_state.historico[indice_real]
                            fotos_antes_atuais = (
                                reg_atual.get("fotos_antes_bytes")
                                or normalizar_lista_fotos(
                                    reg_atual, "fotos_antes_bytes", "foto_antes"
                                )
                            )
                            fotos_depois_atuais = (
                                reg_atual.get("fotos_depois_bytes")
                                or normalizar_lista_fotos(
                                    reg_atual, "fotos_depois_bytes", "foto_depois"
                                )
                            )

                            with st.form(
                                "form_edit_manut_"
                                + tag_codigo
                                + "_"
                                + str(indice_real)
                            ):
                                ec1, ec2, ec3 = st.columns(3)
                                with ec1:
                                    ed_data = st.text_input(
                                        "Data (DD/MM/AAAA)",
                                        value=str(reg_atual.get("data", "")),
                                    )
                                with ec2:
                                    ed_tecnico = st.text_input(
                                        "Técnico Responsável",
                                        value=str(reg_atual.get("tecnico", "")),
                                    )
                                with ec3:
                                    ed_visto = st.text_input(
                                        "Visto / Conferência",
                                        value=str(reg_atual.get("visto", "")),
                                    )

                                ed_period = st.selectbox(
                                    "Tipo de Manutenção / Periodicidade",
                                    OPCOES_CICLO_MANUTENCAO,
                                    index=indice_ciclo_existente(
                                        reg_atual.get("periodicidade", freq_reg)
                                    ),
                                )

                                chk_atual = (
                                    reg_atual.get("checklist")
                                    if isinstance(reg_atual.get("checklist"), dict)
                                    else {}
                                )
                                ed_checklist = {}
                                st.markdown("**Checklist Oficial (Itens 4.1 a 4.18):**")
                                for item_chk in CHECKLIST_PMOC_OFICIAL:
                                    valor_chk = bool(chk_atual.get(item_chk, False))
                                    ed_checklist[item_chk] = st.checkbox(
                                        item_chk,
                                        value=valor_chk,
                                        key="ed_chk_"
                                        + tag_codigo
                                        + "_"
                                        + str(indice_real)
                                        + "_"
                                        + item_chk[:4],
                                    )

                                ed_obs = st.text_area(
                                    "Observações Técnicas / Ocorrências",
                                    value=str(reg_atual.get("obs", "")),
                                )

                                if st.form_submit_button(
                                    "💾 Gravar Alterações de Texto e Checklist"
                                ):
                                    reg_atual["data"] = ed_data.strip()
                                    reg_atual["tecnico"] = ed_tecnico.strip()
                                    reg_atual["visto"] = ed_visto.strip()
                                    reg_atual["periodicidade"] = ed_period
                                    reg_atual["checklist"] = ed_checklist
                                    reg_atual["obs"] = ed_obs.strip()
                                    salvar_dados_disco(st.session_state.historico)
                                    st.cache_data.clear()
                                    st.success(
                                        "✅ Alterações da manutenção gravadas com sucesso!"
                                    )
                                    st.rerun()

                            st.markdown("---")
                            st.markdown("**📸 Editar / Trocar Fotos do Registro:**")
                            fa_col, fd_col = st.columns(2)
                            with fa_col:
                                trocar_antes = st.file_uploader(
                                    "🔄 Trocar fotos do ANTES (substitui as atuais do ANTES)",
                                    type=["png", "jpg", "jpeg"],
                                    accept_multiple_files=True,
                                    key="sub_antes_"
                                    + tag_codigo
                                    + "_"
                                    + str(indice_real),
                                )
                                if trocar_antes and st.button(
                                    "💾 Aplicar Troca Fotos ANTES",
                                    key="btn_sub_antes_"
                                    + tag_codigo
                                    + "_"
                                    + str(indice_real),
                                ):
                                    reg_atual["fotos_antes_bytes"] = [
                                        f.getvalue() for f in trocar_antes
                                    ]
                                    salvar_dados_disco(st.session_state.historico)
                                    st.cache_data.clear()
                                    st.success("✅ Fotos do ANTES substituídas!")
                                    st.rerun()

                                if fotos_antes_atuais and st.button(
                                    "🗑️ Limpar Todas Fotos ANTES",
                                    key="btn_clr_antes_"
                                    + tag_codigo
                                    + "_"
                                    + str(indice_real),
                                ):
                                    reg_atual["fotos_antes_bytes"] = []
                                    salvar_dados_disco(st.session_state.historico)
                                    st.cache_data.clear()
                                    st.success("✅ Fotos do ANTES removidas!")
                                    st.rerun()

                            with fd_col:
                                trocar_depois = st.file_uploader(
                                    "🔄 Trocar fotos do DEPOIS (substitui as atuais do DEPOIS)",
                                    type=["png", "jpg", "jpeg"],
                                    accept_multiple_files=True,
                                    key="sub_depois_"
                                    + tag_codigo
                                    + "_"
                                    + str(indice_real),
                                )
                                if trocar_depois and st.button(
                                    "💾 Aplicar Troca Fotos DEPOIS",
                                    key="btn_sub_depois_"
                                    + tag_codigo
                                    + "_"
                                    + str(indice_real),
                                ):
                                    reg_atual["fotos_depois_bytes"] = [
                                        f.getvalue() for f in trocar_depois
                                    ]
                                    salvar_dados_disco(st.session_state.historico)
                                    st.cache_data.clear()
                                    st.success("✅ Fotos do DEPOIS substituídas!")
                                    st.rerun()

                                if fotos_depois_atuais and st.button(
                                    "🗑️ Limpar Todas Fotos DEPOIS",
                                    key="btn_clr_depois_"
                                    + tag_codigo
                                    + "_"
                                    + str(indice_real),
                                ):
                                    reg_atual["fotos_depois_bytes"] = []
                                    salvar_dados_disco(st.session_state.historico)
                                    st.cache_data.clear()
                                    st.success("✅ Fotos do DEPOIS removidas!")
                                    st.rerun()

                        with st.expander(
                            "➕ Adicionar mais fotos a esta manutenção ("
                            + str(h.get("data", ""))
                            + ")"
                        ):
                            novas_antes = st.file_uploader(
                                "Selecionar fotos adicionais do ANTES",
                                type=["png", "jpg", "jpeg"],
                                accept_multiple_files=True,
                                key="add_antes_" + tag_codigo + "_" + str(idx),
                            )
                            novas_depois = st.file_uploader(
                                "Selecionar fotos adicionais do DEPOIS",
                                type=["png", "jpg", "jpeg"],
                                accept_multiple_files=True,
                                key="add_depois_" + tag_codigo + "_" + str(idx),
                            )
                            if st.button(
                                "💾 Anexar Novas Fotos ao Registro",
                                key="btn_add_fotos_" + tag_codigo + "_" + str(idx),
                            ):
                                if novas_antes or novas_depois:
                                    reg = st.session_state.historico[indice_real]
                                    reg.setdefault("fotos_antes_bytes", [])
                                    reg.setdefault("fotos_depois_bytes", [])
                                    reg["fotos_antes_bytes"].extend(
                                        [f.getvalue() for f in novas_antes]
                                    )
                                    reg["fotos_depois_bytes"].extend(
                                        [f.getvalue() for f in novas_depois]
                                    )
                                    salvar_dados_disco(st.session_state.historico)
                                    st.cache_data.clear()
                                    st.success("Fotos adicionadas com sucesso!")
                                    st.rerun()
                                else:
                                    st.warning("Selecione pelo menos uma foto para anexar.")

                        if st.button(
                            "🗑️ Excluir este Registro Incorreto",
                            key="btn_del_" + tag_codigo + "_" + str(idx),
                        ):
                            del st.session_state.historico[indice_real]
                            salvar_dados_disco(st.session_state.historico)
                            st.cache_data.clear()
                            st.success("Registro excluído com sucesso! Atualizando...")
                            st.rerun()

                    st.markdown("---")
            else:
                st.info("Nenhum histórico cadastrado para este aparelho.")

elif opcao == "🛠️ Registrar Manutenção":
    if not eh_admin:
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("🛠️ Registro de Manutenção Preventiva e Ocorrências (PMOC)")
        instalados = [
            e for e in st.session_state.equipamentos if e["status"] == "Instalado"
        ]
        tags = [e["tag"] + " - " + e["ambiente"] for e in instalados]

        if tags:
            tag_sel = st.selectbox("Selecione o Equipamento:", tags)
            tag_codigo = tag_sel.split(" - ")[0]
            hists_eq_atual = [
                h for h in st.session_state.historico if h.get("tag") == tag_codigo
            ]
            prox_sugerido = proximo_ciclo_esperado(hists_eq_atual)
            idx_ciclo = 1 if prox_sugerido == "Trimestral" else 0
            hoje_formatado = datetime.date.today().strftime("%d/%m/%Y")

            periodicidade = st.selectbox(
                "Tipo de Manutenção / Periodicidade (Conforme PMOC):",
                OPCOES_CICLO_MANUTENCAO,
                index=idx_ciclo,
            )

            itens_padrao = (
                ITENS_PADRAO_TRIMESTRAL
                if "Trimestral" in periodicidade
                else (
                    set() if "Corretiva" in periodicidade else ITENS_PADRAO_SEMESTRAL
                )
            )

            with st.form("form_manutencao", clear_on_submit=True):
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    data_manut = st.text_input(
                        "Data da Manutenção (DD/MM/AAAA)", value=hoje_formatado
                    )
                with col_d2:
                    tecnico = st.text_input(
                        "Técnico Responsável", value="Antônio Sérgio Silva Gomes"
                    )
                with col_d3:
                    visto = st.text_input("Visto / Responsável Conferência", value="")

                st.markdown("---")
                st.subheader("📋 Checklist Oficial do PMOC (Itens 4.1 a 4.18)")
                st.caption(
                    "M = Mensal | T = Trimestral | S = Semestral. Os itens padrão do ciclo selecionado já vêm marcados, e você pode alterar qualquer um."
                )

                checklist_inputs = {}
                for item in CHECKLIST_PMOC_OFICIAL:
                    checklist_inputs[item] = st.checkbox(
                        item, value=(item in itens_padrao), key="chk_" + item[:4]
                    )

                st.markdown("---")
                st.subheader(
                    "📸 Registros Fotográficos (Múltiplas Fotos) e Ocorrências (Seção 6)"
                )
                st.caption("Selecione várias fotos de uma só vez nos campos abaixo.")
                obs = st.text_area("Observações Técnicas / Registro de Ocorrências")

                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    fotos_antes = st.file_uploader(
                        "📷 Fotos do ANTES",
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=True,
                    )
                with col_f2:
                    fotos_depois = st.file_uploader(
                        "📷 Fotos do DEPOIS",
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=True,
                    )

                if st.form_submit_button("💾 Salvar Registro de Manutenção"):
                    st.session_state.historico.append(
                        {
                            "tag": tag_codigo,
                            "data": data_manut,
                            "periodicidade": periodicidade,
                            "tecnico": tecnico,
                            "visto": visto,
                            "checklist": checklist_inputs,
                            "obs": obs,
                            "fotos_antes_bytes": (
                                [f.getvalue() for f in fotos_antes]
                                if fotos_antes
                                else []
                            ),
                            "fotos_depois_bytes": (
                                [f.getvalue() for f in fotos_depois]
                                if fotos_depois
                                else []
                            ),
                        }
                    )
                    salvar_dados_disco(st.session_state.historico)
                    st.cache_data.clear()
                    st.success("✅ Manutenção registrada com sucesso!")
        else:
            st.info("Não há equipamentos instalados no momento.")

elif opcao == "✏️ Editar Previstos":
    if not eh_admin:
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("✏️ Gerenciar, Cadastrar Novos e Substituir Equipamentos")
        st.caption(
            "Use esta tela para registrar dados de um equipamento novo ou atualizar dados do ambiente."
        )

        lista_todos = [
            e["tag"] + " - " + e["ambiente"] + " (" + e["status"] + ")"
            for e in st.session_state.equipamentos
        ]
        tag_sel_ed = st.selectbox(
            "Selecione o Equipamento para Editar ou Substituir:", lista_todos
        )
        tag_codigo_ed = tag_sel_ed.split(" - ")[0]
        equip_ed = next(
            (e for e in st.session_state.equipamentos if e["tag"] == tag_codigo_ed),
            None,
        )

        if equip_ed:
            with st.form("form_edicao_geral"):
                st.write(
                    "**Ambiente:** "
                    + equip_ed["ambiente"]
                    + " | **TAG:** "
                    + equip_ed["tag"]
                )
                novo_nome = st.text_input(
                    "Marca / Modelo do Equipamento",
                    value=limpar_numero_serie(equip_ed["equipamento"]),
                )
                novos_btus = st.text_input(
                    "Potência / Carga Térmica (BTUs)", value=equip_ed["btus"]
                )
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    nova_area = st.text_input(
                        "Área Climatizada (m²)",
                        value=str(equip_ed.get("area_m2") or ""),
                        placeholder="Ex.: 12,50",
                    )
                with col_a2:
                    novo_ocup = st.text_input(
                        "Ocupantes Máximos",
                        value=str(equip_ed.get("ocupantes_max") or ""),
                        placeholder="Ex.: 2",
                    )
                novo_status = st.selectbox(
                    "Status de Instalação",
                    ["Instalado", "Previsto"],
                    index=0 if equip_ed["status"] == "Instalado" else 1,
                )

                if st.form_submit_button("✅ Salvar Alterações"):
                    equip_ed["equipamento"] = limpar_numero_serie(novo_nome)
                    equip_ed["btus"] = novos_btus.strip()
                    equip_ed["numero_serie"] = ""
                    equip_ed["area_m2"] = nova_area.strip()
                    equip_ed["ocupantes_max"] = novo_ocup.strip()
                    equip_ed["status"] = novo_status
                    salvar_equipamentos_disco(st.session_state.equipamentos)
                    st.cache_data.clear()
                    st.success(
                        "Equipamento "
                        + tag_codigo_ed
                        + " atualizado e salvo com sucesso!"
                    )
                    st.rerun()

elif opcao == "🖨️ Etiquetas 5x5 cm (Individual)":
    if not eh_admin:
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("🖨️ Pré-visualização de Etiqueta Individual 5x5 cm")
        lista_eq_qr = [
            e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos
        ]
        tag_sel_qr = st.selectbox("Selecione o Equipamento:", lista_eq_qr)
        equip_sel = next(
            (
                e
                for e in st.session_state.equipamentos
                if e["tag"] == tag_sel_qr.split(" - ")[0]
            ),
            None,
        )
        if equip_sel:
            st.markdown(renderizar_etiqueta_html(equip_sel), unsafe_allow_html=True)

elif opcao == "📑 Lote A4 para Gráfica (Guilhotina)":
    if not eh_admin:
        st.warning("🔒 Área restrita ao Administrador.")
    else:
        st.header("📑 Gerador de Arquivo PDF Pronto para Gráfica (5x5 cm)")
        todas_tags = [
            e["tag"] + " - " + e["ambiente"] for e in st.session_state.equipamentos
        ]
        selecionar_todos = st.checkbox(
            "Selecionar todos os equipamentos cadastrados", value=True
        )
        equipamentos_selecionados = (
            todas_tags
            if selecionar_todos
            else st.multiselect(
                "Selecione os equipamentos:", todas_tags, default=todas_tags[:6]
            )
        )

        if st.button("🚀 Gerar PDF Oficial para Download"):
            if not equipamentos_selecionados:
                st.warning("Selecione pelo menos um equipamento.")
            else:
                with st.spinner("Gerando arquivo PDF..."):
                    try:
                        pdf_buffer = io.BytesIO()
                        doc = SimpleDocTemplate(
                            pdf_buffer,
                            pagesize=A4,
                            leftMargin=1.5 * cm,
                            rightMargin=1.5 * cm,
                            topMargin=1.0 * cm,
                            bottomMargin=1.0 * cm,
                        )
                        story = []
                        celulas_pagina = []

                        estilo_header = ParagraphStyle(
                            "EtqHeader",
                            fontName="Helvetica-Bold",
                            fontSize=7.5,
                            leading=9,
                            textColor=colors.whitesmoke,
                            alignment=1,
                        )
                        estilo_texto = ParagraphStyle(
                            "EtqText",
                            fontName="Helvetica",
                            fontSize=6.0,
                            leading=7.5,
                            textColor=colors.black,
                            alignment=0,
                        )
                        estilo_footer = ParagraphStyle(
                            "EtqFooter",
                            fontName="Helvetica-Bold",
                            fontSize=5.5,
                            leading=7,
                            textColor=colors.black,
                            alignment=1,
                        )

                        style_hdr = TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, -1), colors.black),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("TOPPADDING", (0, 0), (-1, -1), 1),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                            ]
                        )
                        style_etq = TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("TOPPADDING", (0, 0), (-1, -1), 2),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                            ]
                        )
                        style_pag = TableStyle(
                            [
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                            ]
                        )

                        for idx, item_sel in enumerate(equipamentos_selecionados):
                            eq_obj = next(
                                (
                                    e
                                    for e in st.session_state.equipamentos
                                    if e["tag"] == item_sel.split(" - ")[0]
                                ),
                                None,
                            )
                            if eq_obj:
                                celulas_pagina.append(
                                    montar_etiqueta_pdf(
                                        eq_obj,
                                        estilo_header,
                                        estilo_texto,
                                        estilo_footer,
                                        style_hdr,
                                        style_etq,
                                    )
                                )

                            if len(celulas_pagina) == 15 or idx == len(
                                equipamentos_selecionados
                            ) - 1:
                                linhas_tabela = []
                                linha_atual = []
                                for cell in celulas_pagina:
                                    linha_atual.append(cell)
                                    if len(linha_atual) == 3:
                                        linhas_tabela.append(linha_atual)
                                        linha_atual = []
                                if linha_atual:
                                    linha_atual.extend([""] * (3 - len(linha_atual)))
                                    linhas_tabela.append(linha_atual)

                                t_pagina = Table(
                                    linhas_tabela,
                                    colWidths=[5.0 * cm, 5.0 * cm, 5.0 * cm],
                                    rowHeights=[5.0 * cm] * len(linhas_tabela),
                                )
                                t_pagina.setStyle(style_pag)
                                story.append(t_pagina)
                                if idx < len(equipamentos_selecionados) - 1:
                                    story.append(PageBreak())
                                celulas_pagina = []

                        doc.build(story)
                        pdf_buffer.seek(0)
                        st.success("✅ Arquivo PDF gerado com sucesso!")
                        st.download_button(
                            "📥 Baixar PDF Pronto para a Gráfica",
                            data=pdf_buffer,
                            file_name="etiquetas_pmoc_5x5cm_grafica.pdf",
                            mime="application/pdf",
                        )
                    except Exception as e:
                        st.error("Erro ao gerar PDF: " + str(e))

elif opcao == "📊 Dashboard Geral":
    st.header("📊 Painel Geral de Climatização")
    total = len(st.session_state.equipamentos)
    instalados = len(
        [e for e in st.session_state.equipamentos if e["status"] == "Instalado"]
    )
    previstos = len(
        [e for e in st.session_state.equipamentos if e["status"] == "Previsto"]
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Aparelhos", total)
    col2.metric("Instalados e Ativos", instalados)
    col3.metric("Previstos / Futuros", previstos)
    st.markdown("---")
    linhas_dash = []
    for e in st.session_state.equipamentos:
        hists_e = [h for h in st.session_state.historico if h.get("tag") == e["tag"]]
        if hists_e and e["status"] == "Instalado":
            ult_d, prox_d, _, tipo_u, prox_t = calcular_proxima_manutencao(hists_e)
            ciclo_txt = rotulo_ciclo_curto(tipo_u) + " -> " + prox_t
        else:
            ult_d, prox_d, ciclo_txt = "-", "-", "-"
        linhas_dash.append(
            {
                "tag": e["tag"],
                "ambiente": e["ambiente"],
                "equipamento": formatar_equipamento_com_serie(e),
                "btus": e["btus"],
                "area_m2": e.get("area_m2") or "-",
                "ocupantes_max": e.get("ocupantes_max") or "-",
                "status": e["status"],
                "ultima_manutencao": ult_d,
                "proxima_manutencao": prox_d,
                "ciclo": ciclo_txt,
            }
        )
    st.dataframe(pd.DataFrame(linhas_dash), width="stretch")

elif opcao == "📄 Relatório Fiscal A4":
    if not eh_admin:
        st.warning("🔒 O Relatório Fiscal A4 é exclusivo do Administrador.")
    else:
        st.header(
            "📄 Relatório Fiscal Oficial A4 (Completo com Checklists e Todas as Fotos)"
        )
        st.info(
            "ℹ️ Este relatório consolida a relação de equipamentos, o histórico completo de manutenções com os itens verificados no checklist e **todas** as fotografias (Antes e Depois) anexadas em cada manutenção."
        )

        filtrar_periodo = st.checkbox(
            "📅 Filtrar manutenções por período (Data Inicial e Data Final)", value=False
        )
        hoje_data = datetime.date.today()
        inicio_padrao = hoje_data - datetime.timedelta(days=180)
        data_inicio = inicio_padrao
        data_fim = hoje_data

        if filtrar_periodo:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                data_inicio = st.date_input(
                    "Data Inicial", value=inicio_padrao, format="DD/MM/YYYY"
                )
            with col_d2:
                data_fim = st.date_input(
                    "Data Final", value=hoje_data, format="DD/MM/YYYY"
                )
            if data_inicio > data_fim:
                st.warning("⚠️ A Data Inicial não pode ser maior que a Data Final.")

        def dentro_do_periodo(h_item):
            if not filtrar_periodo:
                return True
            try:
                d_reg = datetime.datetime.strptime(
                    str(h_item.get("data", "")).strip(), "%d/%m/%Y"
                ).date()
                return data_inicio <= d_reg <= data_fim
            except Exception:
                return False

        periodo_valido = (not filtrar_periodo) or (data_inicio <= data_fim)

        if periodo_valido and st.button(
            "🚀 Gerar PDF Oficial Completo do Relatório Fiscal"
        ):
            with st.spinner(
                "Compilando relatório fiscal completo com todas as fotos e checklists..."
            ):
                try:
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(
                        pdf_buffer,
                        pagesize=A4,
                        leftMargin=1.5 * cm,
                        rightMargin=1.5 * cm,
                        topMargin=1.5 * cm,
                        bottomMargin=1.5 * cm,
                    )
                    story = []

                    estilo_titulo = ParagraphStyle(
                        "RelTitulo",
                        fontName="Helvetica-Bold",
                        fontSize=14,
                        leading=18,
                        textColor=colors.HexColor("#111111"),
                        alignment=1,
                    )
                    estilo_sub = ParagraphStyle(
                        "RelSub",
                        fontName="Helvetica-Bold",
                        fontSize=10,
                        leading=14,
                        textColor=colors.HexColor("#333333"),
                        alignment=1,
                    )
                    estilo_info = ParagraphStyle(
                        "RelInfo",
                        fontName="Helvetica",
                        fontSize=9,
                        leading=13,
                        textColor=colors.HexColor("#444444"),
                    )
                    estilo_secao = ParagraphStyle(
                        "RelSecao",
                        fontName="Helvetica-Bold",
                        fontSize=12,
                        leading=16,
                        textColor=colors.HexColor("#000000"),
                        spaceBefore=12,
                        spaceAfter=6,
                    )
                    estilo_texto = ParagraphStyle(
                        "RelTexto",
                        fontName="Helvetica",
                        fontSize=8.5,
                        leading=12,
                        textColor=colors.HexColor("#222222"),
                    )
                    estilo_check = ParagraphStyle(
                        "RelCheck",
                        fontName="Helvetica",
                        fontSize=7.5,
                        leading=10,
                        textColor=colors.HexColor("#333333"),
                        leftIndent=10,
                    )

                    style_resumo = TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#000000")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                            ("TOPPADDING", (0, 0), (-1, -1), 3),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                    style_imgs = TableStyle(
                        [
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ]
                    )

                    story.append(
                        Paragraph("<b>INSTITUTO SER CONSCIENTE LTDA</b>", estilo_titulo)
                    )
                    story.append(
                        Paragraph(
                            "PLANO DE MANUTENÇÃO, OPERAÇÃO E CONTROLE - PMOC",
                            estilo_sub,
                        )
                    )
                    story.append(
                        Paragraph(
                            "Lei Federal nº 13.589/2018 | ART CREA-MG: MG20265436050",
                            estilo_sub,
                        )
                    )
                    story.append(Spacer(1, 10))

                    texto_periodo = (
                        data_inicio.strftime("%d/%m/%Y")
                        + " a "
                        + data_fim.strftime("%d/%m/%Y")
                        if filtrar_periodo
                        else "Todo o histórico registrado"
                    )

                    story.append(
                        Paragraph(
                            "<b>Data de Emissão:</b> "
                            + hoje_data.strftime("%d/%m/%Y"),
                            estilo_info,
                        )
                    )
                    story.append(
                        Paragraph(
                            "<b>Período do Relatório:</b> "
                            + escapar_xml(texto_periodo),
                            estilo_info,
                        )
                    )
                    story.append(
                        Paragraph(
                            "<b>Responsável Técnico:</b> Eng. Alessandro Coelho (CREA-MG 238468-D)",
                            estilo_info,
                        )
                    )
                    story.append(
                        Paragraph(
                            "<b>Administrador / Gestor:</b> Antônio Sérgio Silva Gomes",
                            estilo_info,
                        )
                    )
                    story.append(Spacer(1, 10))

                    story.append(
                        Paragraph(
                            "📑 Relação Resumida dos Equipamentos Instalados",
                            estilo_secao,
                        )
                    )
                    instalados_df = [
                        e
                        for e in st.session_state.equipamentos
                        if e["status"] == "Instalado"
                    ]
                    dados_tabela = [
                        [
                            "TAG",
                            "Ambiente",
                            "Equipamento",
                            "BTUs",
                            "Última Manutenção",
                            "Próxima",
                            "Frequência",
                        ]
                    ]

                    for eq in instalados_df:
                        hists_eq = [
                            h
                            for h in st.session_state.historico
                            if h.get("tag") == eq["tag"] and dentro_do_periodo(h)
                        ]
                        if hists_eq:
                            ultima_data, prox_data_str, _, freq_ult, prox_tipo = (
                                calcular_proxima_manutencao(hists_eq)
                            )
                            freq_resumo = (
                                rotulo_ciclo_curto(freq_ult) + " -> " + prox_tipo
                            )
                        else:
                            ultima_data, prox_data_str, freq_resumo = (
                                "Sem registro",
                                "-",
                                "-",
                            )

                        dados_tabela.append(
                            [
                                str(eq.get("tag", "")),
                                str(eq.get("ambiente", "")),
                                formatar_equipamento_com_serie(eq),
                                str(eq.get("btus", "")),
                                str(ultima_data),
                                str(prox_data_str),
                                str(freq_resumo),
                            ]
                        )

                    t_resumo = Table(
                        dados_tabela,
                        colWidths=[
                            1.9 * cm,
                            3.0 * cm,
                            3.0 * cm,
                            1.5 * cm,
                            2.5 * cm,
                            2.3 * cm,
                            2.8 * cm,
                        ],
                    )
                    t_resumo.setStyle(style_resumo)
                    story.append(t_resumo)
                    story.append(Spacer(1, 15))

                    story.append(
                        Paragraph(
                            "📖 Detalhamento Completo, Checklists e Registros Fotográficos",
                            estilo_secao,
                        )
                    )
                    for eq in instalados_df:
                        equip_sem_serie = formatar_equipamento_com_serie(eq)
                        story.append(
                            Paragraph(
                                "<b>📍 Equipamento: "
                                + escapar_xml(eq.get("ambiente", ""))
                                + " (TAG: "
                                + escapar_xml(eq.get("tag", ""))
                                + ")</b> — "
                                + escapar_xml(equip_sem_serie)
                                + " ("
                                + escapar_xml(eq.get("btus", ""))
                                + " BTUs)",
                                estilo_texto,
                            )
                        )
                        hists_eq = [
                            h
                            for h in st.session_state.historico
                            if h.get("tag") == eq["tag"] and dentro_do_periodo(h)
                        ]

                        if hists_eq:
                            for h in hists_eq:
                                freq_reg = h.get("periodicidade", "Semestral")
                                story.append(
                                    Paragraph(
                                        "• <b>Data:</b> "
                                        + escapar_xml(h.get("data", ""))
                                        + " ("
                                        + escapar_xml(freq_reg)
                                        + ") | <b>Técnico:</b> "
                                        + escapar_xml(h.get("tecnico", "")),
                                        estilo_texto,
                                    )
                                )

                                if isinstance(
                                    h.get("checklist"), dict
                                ) and h.get("checklist"):
                                    story.append(
                                        Paragraph(
                                            "  <b>Itens Verificados (PMOC):</b>",
                                            estilo_check,
                                        )
                                    )
                                    for item_nome, status_val in h["checklist"].items():
                                        simbolo = "✓" if status_val else "X"
                                        story.append(
                                            Paragraph(
                                                "    ["
                                                + simbolo
                                                + "] "
                                                + escapar_xml(item_nome),
                                                estilo_check,
                                            )
                                        )

                                if h.get("obs"):
                                    story.append(
                                        Paragraph(
                                            "  <b>Observações:</b> "
                                            + escapar_xml(h["obs"]),
                                            estilo_check,
                                        )
                                    )

                                f_antes = h.get(
                                    "fotos_antes_bytes"
                                ) or normalizar_lista_fotos(
                                    h, "fotos_antes_bytes", "foto_antes"
                                )
                                f_depois = h.get(
                                    "fotos_depois_bytes"
                                ) or normalizar_lista_fotos(
                                    h, "fotos_depois_bytes", "foto_depois"
                                )

                                adicionar_bloco_fotos_pdf(
                                    story,
                                    "  <b>Fotos - ANTES:</b>",
                                    f_antes,
                                    estilo_check,
                                    style_imgs,
                                )
                                adicionar_bloco_fotos_pdf(
                                    story,
                                    "  <b>Fotos - DEPOIS:</b>",
                                    f_depois,
                                    estilo_check,
                                    style_imgs,
                                )
                                story.append(Spacer(1, 6))
                        else:
                            msg_sem = (
                                "  <i>(Nenhuma manutenção registrada no período selecionado)</i>"
                                if filtrar_periodo
                                else "  <i>(Nenhuma manutenção registrada)</i>"
                            )
                            story.append(Paragraph(msg_sem, estilo_texto))
                        story.append(Spacer(1, 8))

                    doc.build(story)
                    pdf_buffer.seek(0)
                    nome_arq = (
                        "relatorio_fiscal_pmoc_"
                        + data_inicio.strftime("%Y%m%d")
                        + "_"
                        + data_fim.strftime("%Y%m%d")
                        + ".pdf"
                        if filtrar_periodo
                        else "relatorio_fiscal_pmoc_completo.pdf"
                    )
                    st.success("✅ Relatório Fiscal Completo em PDF gerado com sucesso!")
                    st.download_button(
                        "📥 Baixar Relatório Fiscal Oficial Completo (PDF)",
                        data=pdf_buffer,
                        file_name=nome_arq,
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error("Erro ao compilar PDF fiscal completo: " + str(e))

if eh_admin:
    st.markdown("---")
    st.subheader("💾 Backup dos Arquivos JSON")
    st.caption(
        "Baixe os dois arquivos e envie para o GitHub para manter seus registros salvos após reinicializações."
    )

    historico_export = []
    for h in st.session_state.historico:
        if not isinstance(h, dict):
            continue
        h_copy = h.copy()
        antes_raw = h_copy.pop("foto_antes_bytes", None)
        depois_raw = h_copy.pop("foto_depois_bytes", None)
        antes_lista = h_copy.get("fotos_antes_bytes") or (
            [antes_raw] if antes_raw else []
        )
        depois_lista = h_copy.get("fotos_depois_bytes") or (
            [depois_raw] if depois_raw else []
        )
        h_copy["fotos_antes_bytes"] = serializar_lista_fotos(antes_lista)
        h_copy["fotos_depois_bytes"] = serializar_lista_fotos(depois_lista)
        historico_export.append(h_copy)

    equipamentos_export = []
    for eq_item in st.session_state.equipamentos:
        eq_clean = eq_item.copy()
        eq_clean["equipamento"] = limpar_numero_serie(eq_clean.get("equipamento", ""))
        eq_clean["numero_serie"] = ""
        equipamentos_export.append(eq_clean)

    json_dados = json.dumps(
        historico_export, ensure_ascii=False, indent=4
    ).encode("utf-8")
    json_equip = json.dumps(
        equipamentos_export, ensure_ascii=False, indent=4
    ).encode("utf-8")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.download_button(
            label="⬇️ Baixar pmoc_dados.json",
            data=json_dados,
            file_name="pmoc_dados.json",
            mime="application/json",
        )
    with col_b2:
        st.download_button(
            label="⬇️ Baixar pmoc_equipamentos.json",
            data=json_equip,
            file_name="pmoc_equipamentos.json",
            mime="application/json",
        )
