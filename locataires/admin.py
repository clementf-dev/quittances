from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.utils.html import format_html
from .models import Locataire, Quittance, Document
from .forms import GenererQuittanceForm, UploadDocumentForm
from calendar import monthrange
from datetime import date

admin.site.site_header = "Gestion des Quittances"
admin.site.site_title = "Quittances"
admin.site.index_title = "Bienvenue"

# ------------------------------
# Admin Locataire
# ------------------------------
@admin.register(Locataire)
class LocataireAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'prenom','paiement_status', 'adresse', 'loyer', 'charges', 'loyer_annuel',
        'generer_quittance_bouton', 'ajouter_document_bouton', 'voir_documents_bouton'
    )

    def paiement_status(self, obj):
        """
        Affiche un symbole coloré selon le statut des quittances du locataire :
        - vert si tous les loyers sont payés
        - orange si au moins un paiement partiel
        - rouge si au moins une quittance impayée
        """
        quittances = obj.quittance_set.all()

        if not quittances.exists():
            return format_html('<span style="color:gray; font-weight:bold;">{}</span>', '⚪')

        # On calcule le statut global
        statut_global = "payé"
        for q in quittances:
            if q.statut_paiement == "impayé":
                statut_global = "impayé"
                break
            elif q.statut_paiement == "partiel":
                statut_global = "partiel"

        if statut_global == "payé":
            color = "green"
            icon = "✅"
        elif statut_global == "partiel":
            color = "orange"
            icon = "🟠"
        else:
            color = "red"
            icon = "❌"

        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, icon)

    paiement_status.short_description = ""  # pas de nom de colonne pour que ce soit juste le symbole
    def generer_quittance_bouton(self, obj):
        return format_html(
            '<a class="button" href="generer-quittance/{}/">📄 Générer quittance</a>',
            obj.id
        )
    generer_quittance_bouton.short_description = "Générer quittance"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generer-quittance/<int:locataire_id>/', self.admin_site.admin_view(self.generer_quittance)),
            path('ajouter-document/<int:locataire_id>/', self.admin_site.admin_view(self.ajouter_document)),
            path('voir-documents/<int:locataire_id>/', self.admin_site.admin_view(self.voir_documents)),
        ]
        return custom_urls + urls

    def generer_quittance(self, request, locataire_id):
        locataire = Locataire.objects.get(id=locataire_id)

        if request.method == "POST":
            form = GenererQuittanceForm(request.POST)
            if form.is_valid():
                mois_num = int(form.cleaned_data['mois'])
                annee = form.cleaned_data['annee']

                dernier_jour = monthrange(annee, mois_num)[1]
                date_debut = date(annee, mois_num, 1)
                date_fin = date(annee, mois_num, dernier_jour)

                loyer = locataire.loyer
                charges = locataire.charges
                total = loyer + charges

                Quittance.objects.get_or_create(
                    locataire=locataire,
                    mois=mois_num,
                    annee=annee,
                    defaults={
                        'date_debut_periode': date_debut,
                        'date_fin_periode': date_fin,
                        'loyer': loyer,
                        'charges': charges,
                        'total': total,
                        'montant_paye': 0
                    }
                )
                self.message_user(request, f"Quittance générée pour {locataire} - {date_debut.strftime('%B %Y')}")
                return redirect(reverse('admin:locataires_quittance_changelist'))
        else:
            form = GenererQuittanceForm(initial={'locataire_id': locataire.id}) # type: ignore

        context = dict(self.admin_site.each_context(request), form=form, locataire=locataire)
        return render(request, "admin/generer_quittance_form.html", context)

    def ajouter_document_bouton(self, obj):
        return format_html('<a class="button" href="ajouter-document/{}/">➕ Ajouter Document</a>', obj.id)
    ajouter_document_bouton.short_description = "Ajouter Document"

    def voir_documents_bouton(self, obj):
        return format_html('<a class="button" href="voir-documents/{}/">📂 Voir Documents</a>', obj.id)
    voir_documents_bouton.short_description = "Voir Documents"

    def ajouter_document(self, request, locataire_id):
        locataire = Locataire.objects.get(id=locataire_id)
        if request.method == 'POST':
            form = UploadDocumentForm(request.POST, request.FILES)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.locataire = locataire
                doc.save()
                self.message_user(request, f"Document ajouté pour {locataire}")
                return redirect(reverse('admin:locataires_locataire_changelist'))
        else:
            form = UploadDocumentForm()
        context = dict(self.admin_site.each_context(request), form=form, locataire=locataire)
        return render(request, "admin/ajouter_document_form.html", context)

    def voir_documents(self, request, locataire_id):
        locataire = Locataire.objects.get(id=locataire_id)
        documents = locataire.documents.all() # type: ignore
        context = dict(self.admin_site.each_context(request), locataire=locataire, documents=documents)
        return render(request, "admin/voir_documents.html", context)


# ------------------------------
# Admin Quittance
# ------------------------------
@admin.register(Quittance)
class QuittanceAdmin(admin.ModelAdmin):
    list_display = (
        'locataire', 'mois_nom', 'annee', 'loyer', 'charges', 'total',
        'montant_paye', 'reste_du', 'statut_colore', 'telecharger_pdf_bouton'
    )
    list_editable = ['montant_paye']

    def mois_nom(self, obj):
        return obj.get_mois_display()
    mois_nom.short_description = "Mois"

    def reste_du(self, obj):
        return obj.reste_du
    reste_du.short_description = "Reste dû"

    def statut_colore(self, obj):
        if obj.statut_paiement == "payé":
            color = "green"
            icon = "✅"
        elif obj.statut_paiement == "partiel":
            color = "orange"
            icon = "🟠"
        else:
            color = "red"
            icon = "❌"
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, icon)
    statut_colore.short_description = "Statut"

    def telecharger_pdf_bouton(self, obj):
        return format_html('<a class="button" href="/quittance/{}/pdf/" target="_blank">📄 Télécharger PDF</a>', obj.id)
    telecharger_pdf_bouton.short_description = "PDF"