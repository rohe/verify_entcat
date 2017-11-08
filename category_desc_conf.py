# Descriptions exists here:
# https://portal.nordu.net/display/SWAMID/Entity+Categories#EntityCategories
# -SFS1993%3A1153

NREN_DESC = (
    "<b>National research and education network</b>(NREN)<br>"
    "The application is provided by the Swedish NREN (SUNET) which is "
    "ultimately responsible for its operation."
    "This category is only relevant for attribute-release between SWAMID "
    "registered IdPs and SUNET services.")

RE_DESC = (
    "<b>Research & Education</b>(RE)<br />"
    "The Research & Education category applies to low-risk services that "
    "support research and education as an essential component. For instance, a "
    "service that provides tools for both multi-institutional research "
    "collaboration and instruction is eligible as a candidate for this "
    "category. This category is very similar to InCommons Research & "
    "Scolarship Category. The recommended IdP behavior is to release name, "
    "eppn, eptid, mail and eduPersonScopedAffiliation which also aligns with "
    "the InCommon recommendation only if the services is also in at least one "
    "of the safe data processing categories. It is also a recommendation that "
    "static organisational information is released.")

SFS_DESC = (
    "<b>Svensk f&ouml;rfattningssamling 1993:1153</b>(SFS)<br />"
    "The SFS 1993:1153 category applies to services that fulfill "
    "<a href='http://www.riksdagen.se/sv/Dokument-Lagar/Lagar/"
    "Svenskforfattningssamling/Forordning-19931153-om-redo_sfs-1993-1153' "
    "target='_blank'>SFS 1993:1153</a>. SFS 1993:1153 limits membership in "
    "this category to services provided by Swedish HEI-institutions, VHS.se or "
    "SCB.se. Example services include common government-operated student- and "
    "admissions administration services such as LADOK and NyA aswell as "
    "enrollment and course registration services. Inclusion in this category "
    "is strictly reserved for applications that are governed by SFS 1993:1153 "
    "which implies that the application may make use of norEduPersonNIN. The "
    "recommended IdP behavior is to release norEduPersonNIN.")

EU_DESC = (
    "<b>EU Adequate Protection</b>(EU)<br />"
    "The application is compliant with any of the EU adequate protection for "
    "3rd countries according to EU Commission decisions on the adequacy of the "
    "protection of personal data in third countries. This category includes "
    "for instance applications that declares compliance with US safe-harbor.")

HEI_DESC = (
    "<b>HEI Service</b>(HEI)<br />"
    "The application is provided by a Swedish HEI which is ultimately "
    "responsible for its operation.")

RS_DESC = (
    "<b>Research & Scholarship</b>(R&S)<br />"
    "Candidates for the Research and Scholarship (R&S) "
    "Category are Service Providers that support research "
    "and scholarship interaction, collaboration or management "
    "as an essential component.")

COC_DESC = (
    "<b>Code of Conduct</b>(CoC)<br />The GEANT Data protection Code of "
    "Conduct (CoC) defines an approach on European level to "
    "meet the requirements of the EU data protection directive for releasing "
    "mostly harmless personal attributes to a Service Provider (SP) from an "
    "Identity Provider (IdP). "
    "For more information please see GEANT Data Protection Code of Conduct. ")

RETURN_CATEGORY = "<br/><br/><b>This category should return the attributes:</b>"

EC_INFORMATION = {
    "": {"Name": "Base category",
         "Description": (
             "<b>Base category</b><br />A basic category.")},
    "coc": {"Name": "CoC", "Description": COC_DESC},
    "nren": {"Name": "NREN", "Description": NREN_DESC},
    "re": {"Name": "RE", "Description": RE_DESC},
    "sfs": {"Name": "SFS", "Description": SFS_DESC},
    "r_and_s": {"Name": "R&S", "Description": RS_DESC},
    "re_eu": {"Name": "RE & EU",
              "Description": RE_DESC + "<br /><br />" + EU_DESC},
    "re_hei": {"Name": "RE & HEI",
               "Description": RE_DESC + "<br /><br />" + HEI_DESC},
    "re_nren": {"Name": "RE & NREN",
                "Description": RE_DESC + "<br /><br />" + NREN_DESC},
    "re_nren_sfs": {
        "Name": "RE & NREN & SFS",
        "Description": RE_DESC + "<br /><br />" + NREN_DESC + "<br /><br />"
                       + SFS_DESC},
    "re_sfs_hei": {
        "Name": "RE & SFS & HEI",
        "Description": RE_DESC + "<br /><br />" + SFS_DESC + "<br /><br />" +
                       HEI_DESC},
}
